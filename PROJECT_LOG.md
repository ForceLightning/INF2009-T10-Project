This document serves to log the progress of the project.

# Project Log
- 2024-02-28: First data collection session conducted at Foodgle. Commits c95789c - df88cc7 were in preparation for data collection. The first machine learning models were trained on just the Wi-Fi data, shown in commit 2407879.
- 2024-03-07: Second data collection session conducted at Foodgle. The team discovered that Foodgle was in the process of relocating to a different part of the campus.
- 2024-03-15: Foodgle relocated to the North side of the campus.
- 2024-03-28: Bluetooth feature extraction completed on the collected data. Commits f03d211 - ec7306c.
- 2024-04-02: Object detection framework using YOLOv8s implemented to retrieve number of persons bounding boxes. Commit 97ee2e3.
- 2024-04-02: Third data collection session conducted at Koufu, this would serve as the validation set to see if methods explored in this project generalise to differing venues.
- 2024-04-02: Linear Regression models were fit to the training data, and generalised well to the Koufu data. Commit fe40869.
- 2024-04-03: Images captured on the Raspberry Pi could have YOLO inference on them directly. Commit 3792ea3.
- 2024-04-03: Edge inferencing and unit tests for them were implemented. Commit 21b85e9.
- 2024-04-03: MQTT communication between the edge and fog was implemented, along with a FastAPI server for end-user device data retrieval. Commit 7d0e2eb.
- 2024-04-04: Sphinx documentation web pages to be built with GitHub actions. Commits af3dc4a - 96710e9.
- 2024-04-04: Live demonstration data loading was implemented. Commit 4bd01cb.
- 2024-04-05: CVE-2024-28219 mitigation. Commit dd9cbca.
- 2024-04-05: Model serialisation and deserialisation implemented for the live demonstration. Commit 8f975fb.
- 2024-04-05: Complete inference pipeline implemented. Commit c3b32bf.
- 2024-04-05: Automatic unit testing with GitHub actions, updated README.md, and implemented a training pipeline for Gaussian Process Regression (GPR). Commit 412eb0a.


# Results

## With only Wi-Fi features
See commit 31fa6b0.
### With only a single edge device as the source
| Model                       | `device_0` $R^2$ | `device_1` $R^2$ | `device_2` $R^2$ | `device_3` $R^2$ |
| --------------------------- | ---------------- | ---------------- | ---------------- | ---------------- |
| Linear Regression           | 0.38             | 0.97             | 0.18             | -2.79            |
| Polynomial Regression       | -160.68          | -0.69            | -3.16            | -5.58            |
| Support Vector Regression   | -0.27            | -0.25            | -0.27            | -0.29            |
| Decision Tree Regressor     | 0.89             | -1.53            | -2.77            | -1.21            |
| Random Forest Regressor     | 0.56             | -0.08            | -1.01            | -0.89            |
| Kernel Ridge Regressor      | -0.02            | 0.92             | 0.29             | -1.87            |
| Linear Ridge Regressor      | 0.38             | 0.97             | 0.18             | -2.78            |
| Gaussian Process Regression | 0.17             | 0.72             | 0.12             | 0.84             |
| Lasso Linear Regressor      | -0.20            | -0.20            | -0.20            | -1.73            |
| Elastic Net Regressor       | -0.20            | -0.20            | -0.20            | -0.20            |

### 3-Fold Cross Validation

| Model                       | $R^2$              |
| --------------------------- | ------------------ |
| Linear Regression           | 0.49, 0.78, 0.00   |
| Polynomial Regression       | 0.45, 0.71, -0.15  |
| Support Vector Regression   | 0.00, 0.00, -0.99  |
| Decision Tree Regressor     | -0.88, 0.79, -1.19 |
| Random Forest Regressor     | 0.12, 0.54, 0.00   |
| Kernel Ridge Regressor      | 0.48, 0.84, 0.01   |
| Linear Ridge Regressor      | 0.49, 0.78, 0.00   |
| Gaussian Process Regression | 0.48, 0.84, 0.01   |
| Lasso Linear Regressor      | 0.79, -0.08, -0.25 |
| Elastic Net Regressor       | 0.32, -0.08, -0.15 |


## With Koufu data as the validation set
See commits fe40859, 4bd01cb, 8f975fb

| Model                       | $R^2$ on training set | $R^2$ on validation set |
| --------------------------- | --------------------- | ----------------------- |
| Linear Regression           | 1.0                   | -1.21                   |
| Gaussian Process Regression | 0.95                  | 0.72                    |
