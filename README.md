# Food-Calories-Prediction-System

#### 1. Problem Statement:

- The calorie content of packed and home-cooked food is rarely obvious to consumers.
- People tracking their diet may find it difficult to estimate calories from nutrition labels at a glance.
- A data-driven system can help predict the calories of a food serving from its nutritional composition.
- The system can provide dietary cautions and recommendations for healthier eating.
- Manual calorie estimation from protein, carbohydrate and fat values is time-consuming and error-prone.


#### 2. Proposed Solution: 
- Collect food-related nutritional information. 
- Validate the entered data. 
- Process the input features required by the Machine Learning model. 
- Use a Random Forest Regression model to predict calories per serving.
- Classify foods based on the predicted calorie value.
- Determine the diet-caution level.
- Generate actionable dietary recommendations using nutritional indicators.
- Display the results through a user-friendly Tkinter interface. 
- Support batch prediction using CSV files.
- Store every user entry and its prediction in a CSV file and a separate Excel file (food_prediction.xlsx).

#### 3. Process Flow:

<p align="center">
  Start
  <br>
  &darr;
  <br>
  Enter Student Details
  <br>
  &darr;
  <br>
  Validate Input
  <br>
  &darr;
  <br>
  Prepare Input Features
  <br>
  &darr;
  <br>
  ML Prediction
  <br>
  &darr;
  <br>
  Determine Performance Level
  <br>
  &darr;
  <br>
  Determine Risk Level
  <br>
  &darr;
  <br>
  Generate Actionable Recommendation
  <br>
  &darr;
  <br>
  Display Result
  <br>
  &darr;
  <br>
  Save Prediction Record
  <br>
  &darr;
  <br>
  End
</p>

#### 4. Project Mapping:

| V-Model Stage           | Smart Student Project                                      |
|:------------------------|:-----------------------------------------------------------|
| Requirement Analysis    | Identify student performance prediction requirements       |
| System Design           | Design ML workflow, application architecture and GUI       |
| Implementation          | Develop Python + ML + Tkinter application                  |
| Integration             | Integrate GUI, trained model and recommendation logic      |
| Testing                 | Test input validation, prediction and batch processing     |
| Validation              | Evaluate model using R², RMSE, MAE and cross-validation    |
| Demonstration           | Present working student performance prediction application |

### Day-Wise Plan

| Day   | Activity |
|:------|:---------|
| Day 1 | Requirement Analysis (+ console prototype, no ML/Tk) |
| Day 2 | System Design + UI (Tkinter frames, layout, events) |
| Day 3 | Implementation (Machine Learning model development) |
| Day 4 | Integration + Testing |
| Day 5 | Validation + Capstone |

### 5. Requirement Analysis
#### 5.1 Functional Requirements
The system should:
+ Accept food details.
+ Accept nutritional indicators (per 100 g).
+ Validate user inputs.
+ Validate nutrient and serving-size ranges.
+ Process input data.
+ Load the trained ML model.
+ Predict calories per serving.
+ Classify foods based on predicted calories.
+ Determine the diet-caution level.
+ Generate actionable dietary recommendations.
+ Display results through the GUI.
+ Handle invalid inputs.
+ Provide a clear/reset option.
+ Provide an exit option.
+ Support batch CSV prediction.
+ Store prediction results (CSV master log + separate XLSX workbook).

#### 5.2 Non Functional Requirements:
The application should be:
+ User-friendly
+ Easy to understand
+ Fast in generating predictions
+ Reliable
+ Maintainable
+ Scalable
+ Robust against invalid inputs
+ Secure with respect to user dietary data
+ Easy to test
+ Suitable for academic demonstration

#### 5.3 Identify the Users
Primary Users may include:
  + Diet-conscious individuals
  + Nutritionists and dietitians
  + Fitness trainers and gym members
  + Health / wellness application developers

#### 5.4 User Requirements
The user should be able to:
+ Enter food and nutrition information.
+ Submit the information for analysis.
+ View the predicted calories for the serving.
+ Understand the food's calorie classification.
+ Understand the diet-caution level.
+ Receive actionable dietary recommendations.
+ Clear the entered information.
+ Process multiple food records using a CSV file.


#### 5.5 Identify System Inputs
The system uses:
+ Food Name
+ Serving Size (g)
+ Protein (g per 100 g)
+ Carbohydrates (g per 100 g)
+ Total Fat (g per 100 g)
+ Dietary Fiber (g per 100 g)
+ Sugars (g per 100 g)

The six nutritional indicators used by the Machine Learning model are:
+ Serving Size (g)
+ Protein (g per 100 g)
+ Carbohydrates (g per 100 g)
+ Total Fat (g per 100 g)
+ Dietary Fiber (g per 100 g)
+ Sugars (g per 100 g)

Food Name is used for identification and record keeping and is not used as an ML feature. Every saved record also gets an automatic Timestamp.

| Parameter | Example |
|:----------|:--------|
| Serving Size | 150 g |
| Protein | 28 g/100 g |
| Carbohydrates | 0 g/100 g |
| Total Fat | 3.6 g/100 g |
| Dietary Fiber | 0 g/100 g |
| Sugars | 0 g/100 g |

#### 5.6 Identify System Outputs
###### 5.6.1 Calorie Prediction
  + Predicted Calories (kcal per serving)
  + Low Calorie
  + Moderate Calorie
  + High Calorie

###### 5.6.2 Additional Outputs
  + Diet-caution level
  + Actionable dietary recommendation
  + Prediction record
  + Batch prediction results

###### Example
__Prediction:__ Moderate Calorie \
__Predicted Calories:__ 197.58 kcal \
__Caution:__ Medium Caution \
__Recommendation:__ Fits into a balanced diet; keep portions consistent with your daily calorie goal.
