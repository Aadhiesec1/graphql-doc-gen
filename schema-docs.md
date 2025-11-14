# GraphQL API Documentation

## Query
Root query type

### Fields
- **user**: `User`
  - Get a user by ID
  - Arguments:
    - **id**: `ID!`
- **posts**: `[Post]`
  - List all posts

## User
A user in the system

### Fields
- **id**: `ID`
  - Unique ID
- **name**: `String`
  - Full name
- **role**: `UserRole`
  - User role

## UserRole
Available user roles

### Enum Values
- `ADMIN` — Administrator user
- `NORMAL` — Regular user

## Post
A post in the system

### Fields
- **id**: `ID`
- **title**: `String`
- **content**: `String`
