# Testing Documentation: MS2-Nollaig

The main README documentation can be found at [README.md](README.md)

[Live Website](https://workout-tracker-ms-project.herokuapp.com/)

## Supported Screens and Browsers

 Unless otherwise stated, all desktop test cases have been carried out across Google Chrome, Firefox, and Microsoft Edge.
All mobile and tablet platform based testing has been performed using Chrome Devtools virtual devices.
The devices I have chosen and their dimensions are:
 1. Galaxy Fold - 280 x 653
 2. Moto G4 - 360 x 640
 3. iPad - 768 x 1024

## Test Cases

### As a new user, I wish to be directed to the appropriate place to register to the Workout Tracker.
- On arrival to the welcome page, the user is met by two messages, one which asks the user to log in if they are returning, and another which invites them to register if they are a new user. There are also navbar links directing the user to the login and registeration pages. If a user navigates to the wrong form by accident, they have another message inviting them to either log in or register, as well as having the navbar links available to use.

### As a new user, I would like to create a personal profile to log my workouts.
- When a new user registers, they can add new workouts to their workout planner page which will only have their planned workouts available to see.

### As a returning user, I want to be able to log in to my own personal user profile.
- When a returning user logs in, they can add new workouts to their workout planner page which will only have their planned workouts available to see. They can also view any completed workouts.

### As a returning user, I want to be able to plan workouts for the future.
- When a returning user logs in, they can add new workouts to their workout planner page which will only have their planned workouts available to see. These can be edited or deleted according to the users needs.

### As a returning user, I want to have the ability to edit planned workouts in case I feel my circumstances have changed.
- A returning user can edit planned workouts according to their needs by clicking the edit button under their chosen workout. This will bring them to an edit workout form.

### As a returning user, I wish to view my previous workouts so that I can compare my exercise progression results.
- A returning user can view their previous completed workouts in the workout history section, and can search by exercise name to return all workouts with that exercise for their perusal.

### As the owner, I want to present an intuitive minimalist style application that allows a user to easily navigate the site.
- This site uses a simple fixed navbar with clear links to indicate their purpose to the user and make it clear the goal of the website. It uses simple colouring and minimal imagery to reduce visual stimuli to a user that may be tracking their workouts while exercising.

### As the owner, the application must be responsive, to allow users to track their workouts as they train, or to have the choice of adding, editing or deleting their workout data from any other device.
- The application is usable on any sized device and navigating the site, a user can move between pages without the use of the browser forward and back buttons. All content is clearly visible and scales correctly to screen size without obscuring any content or overspill.

## Code Validation

### [W3C CSS Validator](https://jigsaw.w3.org/css-validator/#validate_by_input)
Validated my CSS by direct input in to the CSS validator and no errors were found.

### [W3C Markup Validation Service](https://validator.w3.org/#validate_by_input)
- Validated index.html by direct input - one warning: 
   -  The type attribute is unnecessary for JavaScript resources.
Removed the type attribute from line 251 in index.html and re-ran the validator - no errors or warnings to show.
- Validated contact.html by direct input - one error:
    - The value of the for attribute of the label element must be the ID of a non-hidden form control. Changed for attribute to emailaddress and re-ran - no error.

### JSHint
Ran script.js through JSHint, and found no major errors.
![script.js]()

### Chrome Devtools
- Home page:
    1. Desktop
        >  ![Desktop]()
    2. Mobile
        > ![Mobile]()

- Write to Santa page:
    1. Desktop
        > ![Desktop]()
    2. Mobile
        > ![Mobile]()

## Fixed Bugs
