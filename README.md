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
