# **Classmate Directory API Specification v1.1**

Base URL: /api (All API paths are relative to this)  
Data Format: JSON  
Authentication: All authenticated endpoints require a valid credential (e.g., Authorization: Bearer \<token\>) in the request header.

## **1\. Get Student List**

* **Functionality:** Retrieves a list of student (or teacher) records, supporting pagination and basic filtering.  
* **HTTP Method:** GET  
* **Path:** /students  
* **Query Parameters:**  
  * skip (Optional, integer, Default: 0): Number of records to skip for pagination.  
  * limit (Optional, integer, Default: 100): Maximum number of records to return for pagination.  
  * name (Optional, string): Search by name (fuzzy match).  
  * email (Optional, string): Search by email.  
  * position (Optional, string): Filter by position.  
  * *(Other filter fields can be added as needed)*  
* **Request Body:** None  
* **Success Response:**  
  * **Status Code:** 200 OK  
  * **Response Body:** A JSON array of student/teacher objects.  
    \[  
      {  
        "id": 1,  
        "name": "Zhang San", // Example Name  
        "email": "zhangsan@example.com",  
        "phone": "13800138000",  
        "address": "Haidian District, Beijing",  
        "wechat": "zhangsan\_wx",  
        "qq": "123456",  
        "position": "Class Monitor", // New field  
        "comments": "Responsible",  
        "avatar\_url": "https://your-oss-bucket.endpoint/avatars/uuid1.jpg",  
        "created\_at": "2025-04-25T11:20:00Z"  
      },  
      {  
        "id": 3,  
        "name": "Teacher Zhao", // Example Name  
        "email": "zhao.teacher@example.com",  
        "phone": "13700137000",  
        "address": "Haidian District, Beijing",  
        "wechat": "zhao\_teacher",  
        "qq": "888888",  
        "position": "Teacher", // New field, identifies as teacher  
        "comments": "Homeroom Teacher",  
        "avatar\_url": "https://your-oss-bucket.endpoint/avatars/uuid3.jpg",  
        "created\_at": "2025-04-25T10:00:00Z"  
      }  
      // ... other records  
    \]

* **Error Response:**  
  * 401 Unauthorized: Valid authentication credentials were not provided.  
* **Authentication:** Required.

## **2\. Get Specific Student Information**

* **Functionality:** Retrieves detailed information for a single student (or teacher) by their unique ID.  
* **HTTP Method:** GET  
* **Path:** /students/{student\_id}  
* **Path Parameters:**  
  * student\_id (Required, integer): The unique ID of the record to retrieve.  
* **Request Body:** None  
* **Success Response:**  
  * **Status Code:** 200 OK  
  * **Response Body:** A JSON object representing the specified record.  
    {  
      "id": 1,  
      "name": "Zhang San",  
      "email": "zhangsan@example.com",  
      "phone": "13800138000",  
      "address": "Haidian District, Beijing",  
      "wechat": "zhangsan\_wx",  
      "qq": "123456",  
      "position": "Class Monitor", // New field  
      "comments": "Responsible",  
      "avatar\_url": "https://your-oss-bucket.endpoint/avatars/uuid1.jpg",  
      "created\_at": "2025-04-25T11:20:00Z"  
    }

* **Error Responses:**  
  * 401 Unauthorized: Valid authentication credentials were not provided.  
  * 404 Not Found: No record found with the specified ID.  
* **Authentication:** Required.

## **3\. Add New Student (or Teacher)**

* **Functionality:** Creates a new student (or teacher) record, with an option to upload an avatar.  
* **HTTP Method:** POST  
* **Path:** /students  
* **Request Body Format:** multipart/form-data (due to file upload)  
* **Request Body Fields (Form Data):**  
  * name (Required, string): Name.  
  * email (Optional, string): Email address (should be validated).  
  * phone (Optional, string): Phone number.  
  * address (Optional, string): Address.  
  * wechat (Optional, string): WeChat ID.  
  * qq (Optional, string): QQ number.  
  * position (Optional, string): Position (e.g., "Student", "Class Monitor", "Teacher").  
  * comments (Optional, string): Remarks or comments.  
  * avatar (Optional, file): Avatar image file.  
* **Backend Logic:**  
  1. Validate form data.  
  2. If an avatar file exists, upload it to Alibaba Cloud OSS and get the URL.  
  3. Save the information (including avatar\_url and position) to the database.  
  4. Return the newly created record information.  
* **Success Response:**  
  * **Status Code:** 201 Created  
  * **Response Body:** A JSON object representing the newly created record, including the database-assigned id.  
    {  
      "id": 102, // Newly generated ID  
      "name": "Teacher Qian", // Example Name  
      "email": "qian.teacher@example.com",  
      "phone": "13600136000",  
      "address": "Xicheng District, Beijing",  
      "wechat": "qian\_teacher",  
      "qq": "777777",  
      "position": "Teacher", // New field  
      "comments": "Math Teacher",  
      "avatar\_url": "https://your-oss-bucket.endpoint/avatars/uuid\_new\_teacher.jpg", // URL from OSS  
      "created\_at": "2025-04-25T11:30:00Z"  
    }

* **Error Responses:**  
  * 401 Unauthorized: Valid authentication credentials were not provided.  
  * 422 Unprocessable Entity: Request data validation failed (e.g., missing name, invalid email format).  
  * 500 Internal Server Error: File upload failed or other server internal error.  
* **Authentication:** Required.

## **4\. Update Student (or Teacher) Information**

* **Functionality:** Modifies information for an existing record, supporting partial updates and avatar replacement.  
* **HTTP Method:** PATCH (Recommended for partial updates)  
* **Path:** /students/{student\_id}  
* **Path Parameters:**  
  * student\_id (Required, integer): The unique ID of the record to update.  
* **Request Body Format:** multipart/form-data  
* **Request Body Fields (Form Data):** (All fields are optional; provide only the fields to be changed)  
  * name (string): New name.  
  * email (string): New email address.  
  * phone (string): New phone number.  
  * address (string): New address.  
  * wechat (string): New WeChat ID.  
  * qq (string): New QQ number.  
  * position (string): New position.  
  * comments (string): New remarks.  
  * avatar (file): New avatar image file.  
* **Backend Logic:**  
  1. Find the record corresponding to student\_id.  
  2. Check permissions (e.g., can the current user modify this record?).  
  3. Validate the provided form data.  
  4. If a new avatar file is provided, upload it to OSS (potentially deleting the old one) and update the avatar\_url.  
  5. Update the specified fields (including position) in the database.  
  6. Return the complete updated record information.  
* **Success Response:**  
  * **Status Code:** 200 OK  
  * **Response Body:** A JSON object representing the complete updated record.  
    {  
      "id": 1,  
      "name": "Zhang San",  
      "email": "zhangsan@example.com",  
      "phone": "13800138000",  
      "address": "Haidian District, Beijing",  
      "wechat": "zhangsan\_wx",  
      "qq": "123456",  
      "position": "Study Committee Member", // Updated position  
      "comments": "Responsible and excellent grades", // Updated comments  
      "avatar\_url": "https://your-oss-bucket.endpoint/avatars/uuid1.jpg", // URL might be updated  
      "created\_at": "2025-04-25T11:20:00Z" // Creation time usually unchanged  
    }

* **Error Responses:**  
  * 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error.  
* **Authentication:** Required, with appropriate permission checks.

## **5\. Delete Student (or Teacher)**

* **Functionality:** Removes a record based on its ID.  
* **HTTP Method:** DELETE  
* **Path:** /students/{student\_id}  
* **Path Parameters:**  
  * student\_id (Required, integer): The unique ID of the record to delete.  
* **Request Body:** None  
* **Backend Logic:**  
  1. Find the record corresponding to student\_id.  
  2. Check permissions (usually requires administrator privileges).  
  3. Delete the record from the database.  
  4. (Optional) Delete the associated avatar file from Alibaba Cloud OSS.  
* **Success Response:**  
  * **Status Code:** 204 No Content  
  * **Response Body:** None  
* **Error Responses:**  
  * 401 Unauthorized, 403 Forbidden, 404 Not Found.  
* **Authentication:** Required, typically with administrator privileges.

