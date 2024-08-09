To achieve the separation of environments (stage and local) and to use H2 DB for the local environment, we need to make the following changes:

1. Create a new `application-local.yml` configuration file for the local environment.
2. Modify the existing `application.yml` to be used for the stage environment.
3. Update the `run.sh` script to handle both environments.

Let's start with the changes:

### 1. Create `application-local.yml` for the local environment

```diff
--- /dev/null
+++ src/main/resources/application-local.yml
@@ -0,0 +1,13 @@
+spring:
+  datasource:
+    url: jdbc:h2:mem:testdb
+    driver-class-name: org.h2.Driver
+    username: sa
+    password: password
+  h2:
+    console:
+      enabled: true
+  jpa:
+    hibernate:
+      ddl-auto: update
+    show-sql: true
```

### 2. Modify `application.yml` to be used for the stage environment

```diff
--- src/main/resources/application.yml
+++ src/main/resources/application.yml
@@ -1,13 +1,13 @@
 spring:
   datasource:
-    url: jdbc:postgresql://<RDS_ENDPOINT>:5432/<DB_NAME>
-    username: <DB_USERNAME>
-    password: <DB_PASSWORD>
+    url: jdbc:postgresql://stage-rds-endpoint:5432/stage_db
+    username: stage_user
+    password: stage_password
     driver-class-name: org.postgresql.Driver
   jpa:
     hibernate:
       ddl-auto: update
     show-sql: true
     properties:
       hibernate:
         format_sql: true
```



### 6. Update `application.yml` to include profile-specific configurations

```diff
--- src/main/resources/application.yml
+++ src/main/resources/application.yml
@@ -1,13 +1,15 @@
 spring:
   profiles:
-    active: stage
+    active: stage
   datasource:
-    url: jdbc:postgresql://<RDS_ENDPOINT>:5432/<DB_NAME>
-    username: <DB_USERNAME>
-    password: <DB_PASSWORD>
+    url: jdbc:postgresql://stage-rds-endpoint:5432/stage_db
+    username: stage_user
+    password: stage_password
     driver-class-name: org.postgresql.Driver
   jpa:
     hibernate:
       ddl-auto: update
     show-sql: true
     properties:
       hibernate:
         format_sql: true
```

### 7. Update `application-local.yml` to include profile-specific configurations

```diff
--- src/main/resources/application-local.yml
+++ src/main/resources/application-local.yml
@@ -1,13 +1,15 @@
 spring:
   profiles:
-    active: local
+    active: local
   datasource:
-    url: jdbc:h2:mem:testdb
-    driver-class-name: org.h2.Driver
-    username: sa
-    password: password
+    url: jdbc:h2:mem:testdb
+    driver-class-name: org.h2.Driver
+    username: sa
+    password: password
   h2:
     console:
       enabled: true
   jpa:
     hibernate:
       ddl-auto: update
     show-sql: true
```
