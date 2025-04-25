# **API Request Examples (using curl)**

This document provides examples of how to interact with the Classmate Directory API using the curl command-line tool.  
**Assumptions:**

* **Base URL:** https://yourdomain.com/api  
* **Authentication:** You have a valid authentication token (e.g., JWT) represented as YOUR\_AUTH\_TOKEN. Replace this placeholder with your actual token.  
* **File Paths:** Replace /path/to/local/avatar/... with the actual path to image files on your machine when testing uploads.

## **1\. Get Student List (GET /students)**

### **Basic Request (Default Limit)**

curl \-X GET "https://yourdomain.com/api/students" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN"

### **Request with Pagination (Get records 11-20)**

curl \-X GET "https://yourdomain.com/api/students?skip=10\&limit=10" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN"

### **Request with Name Filter**

curl \-X GET "https://yourdomain.com/api/students?name=Zhang" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN"

### **Request with Position Filter**

curl \-X GET "https://yourdomain.com/api/students?position=Teacher" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN"

## **2\. Get Specific Student Information (GET /students/{student\_id})**

### **Get Student with ID 42**

curl \-X GET "https://yourdomain.com/api/students/42" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN"

## **3\. Add New Student (POST /students)**

### **Add Student with Avatar**

*Note: Use @ followed by the local file path for file uploads.*  
curl \-X POST "https://yourdomain.com/api/students" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN" \\  
     \-H "Content-Type: multipart/form-data" \\  
     \-F "name=Wang Wu" \\  
     \-F "email=wangwu@example.com" \\  
     \-F "phone=13912345678" \\  
     \-F "position=Student" \\  
     \-F "comments=New student in class 3" \\  
     \-F "avatar=@/path/to/local/avatar/wangwu.jpg"

### **Add Student without Avatar**

curl \-X POST "https://yourdomain.com/api/students" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN" \\  
     \-H "Content-Type: multipart/form-data" \\  
     \-F "name=Zhao Liu" \\  
     \-F "email=zhaoliu@example.com" \\  
     \-F "position=Teacher"

## **4\. Update Student Information (PATCH /students/{student\_id})**

### **Update Name, Position, and Avatar for Student ID 1**

curl \-X PATCH "https://yourdomain.com/api/students/1" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN" \\  
     \-H "Content-Type: multipart/form-data" \\  
     \-F "name=Zhang San Updated" \\  
     \-F "position=Study Committee Member" \\  
     \-F "avatar=@/path/to/new/avatar.png"

### **Update Only Comments for Student ID 5**

curl \-X PATCH "https://yourdomain.com/api/students/5" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN" \\  
     \-H "Content-Type: multipart/form-data" \\  
     \-F "comments=Updated remarks here."

## **5\. Delete Student (DELETE /students/{student\_id})**

### **Delete Student with ID 15**

curl \-X DELETE "https://yourdomain.com/api/students/15" \\  
     \-H "Authorization: Bearer YOUR\_AUTH\_TOKEN"  

