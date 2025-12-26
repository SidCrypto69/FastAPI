from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Annotated, Literal, Optional
from datetime import date
import json
 
app = FastAPI()

class MedicalHistory(BaseModel):
    conditions: list[str] = Field(default_factory=list, description='List of medical conditions')
    surgeries: list[str] = Field(default_factory=list, description='List of surgeries undergone')
    medications: list[str] = Field(default_factory=list, description='List of medications taken and Current dosses')
    allergies: list[str] = Field(default_factory=list, description='List of allergies')


class patient(BaseModel):
    id: Annotated [str, Field(..., description='ID of the patient', examples=['P001'])] 
    name: Annotated [str, Field(..., description='Name of the patient')] 
    city: Annotated[str, Field(..., description='City of the patient')]
    age: Annotated[int , Field(..., gt=0, description='Age of the patient in years')]
    gender: Annotated[Literal['Male','Female','Others'], Field(..., description= 'Gender of the Patient')]
    height: Annotated[float, Field(..., gt=0, description='Patients height in mts')] 
    weight: Annotated[float, Field(..., gt=0, description='Patients weight in KGs')]
    phone: Annotated[str, Field (..., description='Phone number of the patient')]
    email: Annotated[Optional[str], Field(default=None, description='Email Address')]
    smoker : Annotated[Literal['Yes','No'], Field(..., description='Is the patient a smoker')]
    last_visit_date: Annotated[Optional[str], Field(default=None, description='Last visit date')]
    medical_history: Annotated[Optional[MedicalHistory], Field(default=None, description='Medical history of the patient')]
    activity_level: Annotated[Literal['Low','Medium','High'], Field(..., description='Activity level of the patient')]
    
    @field_validator('gender', 'smoker', 'activity_level', mode='before')
    @classmethod
    def normalize_case(cls, v):
        return v.strip().capitalize() if isinstance(v, str) else v

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
         if self.bmi < 18.5:
           return 'Underweight'
         elif self.bmi < 25:
              return 'Normal'
         elif self.bmi < 30:
             return 'Overweight'
         else:
            return 'Obese'    

class patientupdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['Male','Female','Others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    phone: Annotated[Optional[str], Field(default=None)]
    email: Annotated[Optional[str], Field(default=None)]
    smoker: Annotated[Optional[Literal['Yes','No']], Field(default=None)]
    last_visit_date: Annotated[Optional[str], Field(default=None)]
    medical_history: Annotated[Optional[MedicalHistory], Field(default=None)]
    activity_level: Annotated[Optional[Literal['Low','Medium','High']], Field(default=None)]

    @field_validator('gender', 'smoker', 'activity_level', mode='before')
    @classmethod
    def normalize_case(cls, v):
        return v.strip().capitalize() if isinstance(v, str) else v

def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def root():
    return {"message": "patient health management system api"}

@app.get("/about")
def about():
    return{"message": "A fully functional API to manage patient health data and provide insights based on BMI calculations."}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description = 'ID of the patient in the DB', example='P001')):
    # load data from JSON file
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description= 'Field to sort by', example='age'), order: str = Query('asc', description= 'sort in asc or desc order')):
    
    valid_fields = ['height', 'weight', 'bmi', 'age']

    if sort_by not in valid_fields:
        raise HTTPException (status_code = 400, detail=f'Invalid field select from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException (status_code = 400, detail='Order must be either asc or desc')
    
    data = load_data()
    sort_order = False if order == 'asc' else True

    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by,0), reverse= sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: patient):
    #load existing data from JSON file
    data= load_data()

    #Check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code = 400, detail='patient already exsits')
        
    #new patient add to the database
    data[patient.id]= patient.model_dump(exclude= ['id'])

    #save updated data back to JSON file
    save_data(data)

    return JSONResponse(content={'message':'patient added sucessfully'}, status_code= 201)

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: patientupdate):
    # load existing data from JSON file
    data = load_data()

     #check if the patient exsits or not
    if patient_id not in data:
        raise HTTPException(status_code= 404, detail='Patient not found')
    
    #retrieve the existing patient data
    existing_patient = data[patient_id]

    #converting the pydantic object model to a dictionary and put it in a variable
    updated_patient_data = patient_update.model_dump(exclude_unset = True)

    #if medical_history is a full object, replace/update it ~ just to update the fields in the medical history object but not complete replace it
    if 'medical_history' in updated_patient_data and updated_patient_data['medical_history']:
        mh = updated_patient_data.pop('medical_history')
        existing_mh = existing_patient.get('medical_history') or {}
        existing_patient['medical_history'] = {**existing_mh, **mh}

    #creating a for loop to update exsiting data with key value pair format
    for key, value in updated_patient_data.items():
        existing_patient[key] = value

    #create a pydantic object on exisiting data and update the bmi and verdict
    existing_patient ['id']= patient_id
    patient_pydantic_object = patient(**existing_patient)

    #convert pydantic object back to a dictionary
    existing_patient = patient_pydantic_object.model_dump(exclude='id')
    # add this dict to data
    data[patient_id] = existing_patient

    #save the data
    save_data(data)

    return JSONResponse(content={'message':'patient updated successfully'}, status_code= 200)

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    # load existing data from JSON file
    data = load_data()

    #check if the patient exsits or not
    if patient_id not in data:
        raise HTTPException(status_code= 404, detail='Patient not found')

    #delete the patient
    del data[patient_id]

    #save the data
    save_data(data)

    return JSONResponse(content={'message':'patient deleted successfully'}, status_code= 200)
