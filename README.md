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
