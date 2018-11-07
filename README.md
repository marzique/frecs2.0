# WebSite_project
RT Website
ON AIR: https://rt-rpd.herokuapp.com/

![image](https://user-images.githubusercontent.com/25755345/44372331-0bae2780-a4ec-11e8-8409-6e9e11f2005b.png)
![image](https://user-images.githubusercontent.com/25755345/44538904-5954ab00-a70b-11e8-89ce-23478a1cef28.png)
![image](https://user-images.githubusercontent.com/25755345/44602615-c4c07a80-a7e8-11e8-8494-25e3fbb80c22.png)

# RBAC (Role Based Access Control)
User --> Role --> Permissions(Rights)
- fresh users will have 'not-confirmed' role with limited rights until they confirm their email address.
- after email confirmation users will have 'confirmed' role with a little more rights and views
- next step is 2 branches 'student' or 'teacher', both will be assigned by colleagues. 
  student - by the head of the group, teacher by another 'teacher'. (Also there's option to give tokens which can be used when registering to confirm either role)
- next we should have 'editor' role for those who can add new posts/conferences and delete them.
- 'admin' and 'moderator' roles for those who will support website.
