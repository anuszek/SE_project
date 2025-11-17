# Access Control System (QR + Face Biometrics)
~~Project made for Software Engineering class~~

## Project Description

This is the repository for the **Access Controll System** system, which aims to increase the security and reliability of employee entry registration at a facility. The system uses two-factor authentication, combining the scanning of a QR code access pass with real-time biometric verification of the employee's face.

The system is designed to eliminate abuse (e.g., sharing access cards), ensure reliable work time tracking, and provide automatic reporting on incidents.

## Main Features

* **Two-Factor Authentication:** Access is granted only when the scanned QR code matches the detected employee's face (1:1 match).

* **Abuse Detection:** The system automatically identifies and logs discrepancies (e.g., correct QR, but incorrect face) as incidents.

* **Employee Management:** An admin panel for adding/removing employees, managing their permissions, and adding reference photos.

* **Reporting Module:** Generation of reports for correct entries and incidents, with options for filtering and exporting.

* **Incident Notifications:** Automatic alerts for the security department in case a high-risk entry attempt is detected.

## Key System Parameters

* **Hardware Platform:** The system is intended to run on a laptop (CPU/GPU) with an integrated camera.

* **Performance:** Full verification (QR + face) should not exceed **3 seconds**.

* **Accuracy:** The required minimum identification accuracy is **90%**.

* **Scale:** The system is designed to support up to **20 employees**.

* **Data Storage:** System logs and incident reports are stored for **6 months**.
