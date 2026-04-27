# Module 14 Reflection

For this module I extended the calculator API from the earlier authentication work into a user-specific calculation manager. The main change was making the calculation BREAD endpoints depend on the logged-in user instead of accepting a user id from the request body. That makes browse, read, edit, add, and delete safer because one user cannot see or modify another user's calculations.

The backend work built on the Module 12 and Module 13 structure. Module 12 already had calculation BREAD routes, and Module 13 added JWT login and registration. Module 14 combines both ideas by requiring a bearer token on calculation endpoints and using the token subject to choose the database records. I also added PATCH support for partial edits and kept PUT for the assignment requirement.

The front-end work was a bigger step because the previous module only had login and registration pages. I added a calculations page that uses the JWT stored in localStorage. The page validates numbers, valid operation types, and divide-by-zero before sending requests. It also supports the full BREAD flow from the browser: browse the table, read a calculation detail, edit a row, add new records, and delete records.

Testing helped catch the most important behavior. The integration tests cover successful BREAD operations, invalid inputs, missing tokens, invalid tokens, and attempts to access another user's calculations. The Playwright tests cover registration/login validation and the calculation page workflow from the browser.

The main challenge was separating the older user_id-based API behavior from the newer authenticated behavior. Letting the client choose a user_id is easy to test, but it is not secure. The better approach was to ignore user_id for calculation creation and always assign the logged-in user's id from the token. That made the backend behavior match the security requirement more closely.

The CI/CD workflow continues the same DevOps pattern from the previous module. It runs the tests, builds the Docker image, pushes to Docker Hub, and scans the final image. This keeps the project repeatable and gives a clear proof point for the submission screenshots.
