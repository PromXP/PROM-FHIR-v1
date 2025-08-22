import uuid
from fastapi import  BackgroundTasks, Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Query, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from db import admin_lobby, build_admin_fhir_bundle, convert_patientbase_to_fhir, convert_patientmedical_to_fhir, convert_to_patientcontact_fhir_bundle,doctor_lobby, generate_fhir_bundle, generate_fhir_doctor_bundle, get_collection, post_surgery_to_fhir_bundle, users_collection, patient_data,patient_base ,patient_contact ,patient_medical,patient_surgery_details 
from models import Admin, Doctor, PatientBase, PatientContact, PatientMedical, PostSurgeryDetail, QuestionnaireAssignment, QuestionnaireScore
from datetime import datetime, timezone
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Message": "use '/docs' endpoint to find all the api related docs "}

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

@app.post("/registeradmin")
async def register_admin(admin: Admin):
    # Check if user already exists
    existing = await users_collection.find_one({
        "$or": [
            {"email": admin.email},
            {"phone_number": admin.phone_number},
            {"uhid": admin.uhid}
        ]
    })
    if existing:
        raise HTTPException(status_code=400, detail="User with this email, phone number, or UHID already exists.")

    # Store in admin_lobby (FHIR formatted)
    fhir_bundle = build_admin_fhir_bundle(admin)
    fhir_result = await admin_lobby.insert_one(fhir_bundle)

    # Store login credentials separately in users collection
    user_record = {
        "email": admin.email,
        "phone_number": admin.phone_number,
        "uhid": admin.uhid,
        "password": admin.password,
        "type": "admin",
        "created_at": now
    }
    await users_collection.insert_one(user_record)

    return {
        "message": "Admin registered successfully",
        "admin_id": str(fhir_result.inserted_id)
    }


@app.post("/registerdoctor")
async def register_doctor(doctor: Doctor):
    # Check for duplicates
    existing = await users_collection.find_one({
        "$or": [
            {"email": doctor.email},
            {"phone_number": doctor.phone_number},
            {"uhid": doctor.uhid}
        ]
    })
    if existing:
        raise HTTPException(status_code=400, detail="User with this email, phone number, or UHID already exists.")

    # Check if admin who created this doctor exists
    admin_exists = await users_collection.find_one({
        "email": doctor.admin_created,
        "type": "admin"
    })
    if not admin_exists:
        raise HTTPException(status_code=404, detail="Admin who created this doctor does not exist.")

    # Generate and store FHIR-compliant doctor bundle
    doctor_bundle = generate_fhir_doctor_bundle(doctor)
    result = await doctor_lobby.insert_one(doctor_bundle)

    # Store in users collection
    user_record = {
        "email": doctor.email,
        "phone_number": doctor.phone_number,
        "uhid": doctor.uhid,
        "password": doctor.password,
        "type": "doctor",
        "created_at": now
    }
    await users_collection.insert_one(user_record)

    # Update doctors_created list in admin_lobby if needed
    await admin_lobby.update_one(
        {"entry.resource.identifier.value": doctor.admin_created},
        {"$push": {"doctors_created": doctor.email}}
    )

    return {
        "message": "Doctor registered successfully",
        "doctor_id": str(result.inserted_id)
    }

# @app.post("/post_patient/")
# async def post_patient_to_db(patient: Patient):
#     try:
#         fhir_patient = convert_patient_to_fhir(patient)  # corrected function name
#         patient_data.insert_one(fhir_patient)
#         return {
#             "status": "success",
#             "message": "Patient data saved in FHIR format."
#         }
#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/patients-base")
async def create_patient(patient: PatientBase):
    # Check if patient already exists
    existing = await patient_base.find_one({"id": patient.uhid})
    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")

    # Convert to FHIR Bundle
    fhir_data = convert_patientbase_to_fhir(patient)

    # Store in MongoDB
    result = await patient_base.insert_one(fhir_data)

    return {
        "message": "Patient created successfully",
        "patient_id": patient.uhid  # Use patient.uhid directly
    }

@app.post("/fhir/store-patient-contact")
async def store_patient_contact(contact: PatientContact):
    # Convert to FHIR Bundle
    fhir_bundle = convert_to_patientcontact_fhir_bundle(contact)

    # Store the FHIR Bundle in the database
    await patient_contact.insert_one(fhir_bundle)

    return {
        "message": "Patient contact stored successfully"
    }

@app.post("/fhir/store-patient-medical")
async def store_patient_medical(data: PatientMedical):
    fhir_bundle = convert_patientmedical_to_fhir(data)

    result = await patient_medical.insert_one(fhir_bundle)

    return {
        "status": "success" if result.inserted_id else "error",
        "uhid": data.uhid
    }

# ---------- POST: Assign Questionnaire ----------
@app.post("/assign-questionnaire")
async def assign_questionnaire(data: QuestionnaireAssignment):
    collection = get_collection(data.side)

    # Find existing bundle by UHID in Patient resource's text.div (regex search)
    existing = await collection.find_one({
        "entry.resource.resourceType": "Patient",
        "entry.resource.text.div": {"$regex": data.uhid, "$options": "i"}
    })

    if existing:
        # Extract Patient UUID from existing bundle
        patient_uuid = None
        for entry in existing.get("entry", []):
            res = entry.get("resource", {})
            if res.get("resourceType") == "Patient":
                patient_uuid = res.get("id")
                break
        if not patient_uuid:
            # Defensive fallback: generate a new UUID (shouldn't happen)
            patient_uuid = str(uuid.uuid4())

        # Check for duplicate name+period in existing entries
        for entry in existing.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") in ["Task", "QuestionnaireResponse", "Observation"]:
                if resource.get("resourceType") == "Observation":
                    code_text = resource.get("code", {}).get("text", "")
                    value_str = resource.get("valueString", "")
                    if (code_text == data.name and f"({data.period})" in value_str):
                        return {"message": "Questionnaire already assigned for this period"}
                else:
                    if resource.get("description") == f"{data.name} - {data.period}":
                        return {"message": "Questionnaire already assigned for this period"}

        # Generate new entries but exclude Patient resource
        new_bundle = generate_fhir_bundle([data], existing_patient_uuid=patient_uuid, patient_id=data.uhid.lower())
        new_entries = [
            e for e in new_bundle["entry"]
            if e["resource"]["resourceType"] != "Patient"
        ]

        # Append new entries to existing bundle's entry list
        await collection.update_one(
            {"_id": existing["_id"]},
            {"$push": {"entry": {"$each": new_entries}}}
        )

        return {"message": "Questionnaire assigned successfully"}

    else:
        # No existing bundle, create a new one with patient + questionnaire
        fhir_bundle = generate_fhir_bundle([data])
        await collection.insert_one(fhir_bundle)

        return {"message": "Questionnaire assigned successfully"}



# ---------- PUT: Add Score ----------
@app.put("/add-score")
async def add_score(data: QuestionnaireScore):
    collection = get_collection(data.side)

    # Find patient bundle by UHID in Patient resource's text.div
    bundle = await collection.find_one({
        "entry.resource.resourceType": "Patient",
        "entry.resource.text.div": {"$regex": data.uhid, "$options": "i"}
    })

    if not bundle:
        raise HTTPException(status_code=404, detail="Patient bundle not found")

    updated = False
    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        if (
            res.get("resourceType") == "Observation"
            and res.get("subject", {}).get("reference", "").startswith("urn:uuid:")
            and res.get("code", {}).get("text") == data.name
            and f"({data.period})" in res.get("valueString", "")
        ):
            res["valueString"] = f"Scores ({data.period}): {', '.join(str(s) for s in data.score)}"
            res["status"] = "final"
            res["effectiveDateTime"] = data.timestamp
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Observation not found for update")

    await collection.update_one({"_id": bundle["_id"]}, {"$set": {"entry": bundle["entry"]}})

    return {"message": "Score updated successfully"}

@app.post("/surgery_details")
async def create_surgery_details(details: PostSurgeryDetail):
    try:
        fhir_bundle = post_surgery_to_fhir_bundle(details)
        to_insert = jsonable_encoder(fhir_bundle)

        result = await patient_surgery_details.insert_one(to_insert)  # <-- await here!

        return {"inserted_id": str(result.inserted_id), "message": "Surgery details stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing surgery details: {str(e)}")