# Sprint 3 - Developing a Minimum Viable Product (MVP)


## Sprint Goals

Continue to develop the web application to the point that it provides all key functionality of the system. Test and refine it so that it can serve as the basis for the final phase of development.

### Specific Goals

- Create the following web pages:
    - Dynamic Home Page for each user type
    - Participating polls
    - Creating Polls
    - Poll Details
    - Editing polls
    - Dynamic Profile
- Develop SQL database queries to:
    - Create Polls
    - Update Poll/User Information
    - Delete Poll/User data

## Testing Creating Polls / Participants

When creating a poll, I need the script to collect information from the form and insert it into the database, if the creator has selected the poll to not be public and has chosen a specific number of participants, the script needs to get a list of the users and get a random sample of that specific size to use as participants for that poll.

Route:

![Poll Creation Route](screenshots/sprint3/poll-create-route.png)

![Test of Participating Page](screenshots/sprint3/participating-test-display.png)

Testing it with 2 random participants and checking my 'participating' page as one of the two regular user accounts showed that displaying the data worked as intended but when I went as the second account, they were not a participant of the poll, and comparing with the database it showed that user[0] (the admin) was the other participant. The participants should only be normal users and not admins or creators as they cannot vote on polls.

![DB Participants Issue](screenshots/sprint3/invalid-participants.png)


### Changes / Improvements

I fixed this by adding a filter that goes through each user and if they are not an admin or creator adds them to a useable list for the random sample.

![User Participant Filter](screenshots/sprint3/updated-participant-selection.png)

![DB Participants Fixed](screenshots/sprint3/valid-participants.png)

Testing this again multiple times, it worked and the correct users [2]&[3] were selected each time, I also ensured that the poll creation page limited the number of possible participants to the count of valid participants which prevents the script from attempting to reach out of bounds.

After this, I added more seed data (3 users, 2 polls) for testing.

## Testing Home Page

The Home page is dynamic based on the users account type:

- For Users, logged in or not it shows all public polls however if they are not logged in they cannot vote or comment.
- For Admins, they can see all polls and manage users and comments.
- For Creators, they can see their own polls, public or not and edit them.

Home Page [Logged Out]:

![Display of Home Page (Logged Out)](screenshots/sprint3/home-logged-out.png)

Home Page [User]:

![Display of Home Page (User)](screenshots/sprint3/home-user.png)

Home Page [Admin]:

![Display of Home Page (Admin)](screenshots/sprint3/home-admin.png)

Home Page [Creator]:

![Display of Home Page (Creator)](screenshots/sprint3/home-creator.png)

I tested this system with my end user and they thought it worked well but they said that the creator should be able to comment on their own public polls to engage with the community.

### Changes / Improvements

I added the comment code from the users section so that the creators are able to comment on their own posts.

![Alt text](screenshots/sprint3/comment-html.png)

![Display of Changed Home Page (Creator)](screenshots/sprint3/home-creator-updated.png)



## Testing Profiles

Testing my dynamic profile page in all of its different states;
 - If the user is viewing their own profile, show it editable.

![Alt text](screenshots/sprint3/own-profile.png)

 - If the user is viewing another users profile, block them.

![Alt text](screenshots/sprint3/invalid-permissions.png)

 - If the user is viewing a creators profile, show them their public facing polls and details.

![Alt text](screenshots/sprint3/creators-profile.png)

 - If the user is an admin, always allow them to edit a profile.

![Alt text](screenshots/sprint3/admin-view-error.png)

All of these outcomes except the admin view work correctly with the right checks and displaying. The admin view does not display correctly when looking at a user profile, though it does work when viewing a creator profile.

### Changes / Improvements

I fixed the admin view for viewing regular users by adding an extra section to the template for admins viewing a regular user profile.

![alt text](screenshots/sprint3/admin-profile-view.png)

Testing this with my end user they suggested that I display the users comments to the admin for moderation.

![alt text](screenshots/sprint3/admin-profile-view-updated.png)


## Testing Images

I added an images system for both the users and polls. Users can edit their profile pictures once they have created an account and creators are able to add images to their polls.

![Alt text](screenshots/sprint3/poll-image-test.gif)

![Alt text](screenshots/sprint3/poll-image-route.png)

![Alt text](screenshots/sprint3/image-insertion.png)

The Image is correctly added to the uploads folder and the database, displaying correctly on the website.

### Changes / Improvements

I also tested this again with my end-user on the users accounts and it worked as intended, but my end-user suggested I add a default image to the user profile. I added this to my config and tested it by creating a new user.

![Alt text](screenshots/sprint3/table-default.png)

![Alt text](screenshots/sprint3/default-image-test.gif)

Testing this new addition it works correctly and my end-user liked the change.


## Testing Editing

Testing of the routes for editing users and polls.

The editing poll page is almost identical to the create poll form however the editing user profile is different to the sign up form.

Editing Poll

![alt text](screenshots/sprint3/edit-poll-test.gif)

Editing User

![alt text](screenshots/sprint3/edit-user-test.gif)

Both work well and testing them with the end-user they were happy with the options.

## Testing Deleting

Testing deleting users and polls, including images.

Deleting both requires a SQL query to remove the related entries from the database and then reference the image and delete it from the uploads folder.

Deleting Polls

![alt text](screenshots/sprint3/delete-poll-test.gif)

![alt text](screenshots/sprint3/poll-delete-terminal.png)

Deleting Polls works as intended with each relevant entry removed from the database.

Deleting Users

![alt text](screenshots/sprint3/delete-user-test.gif)

Deleting the user works correctly, but when testing deleting a profile where the profile image was the default, the script would delete the image from the folder and cause issues for most of the other users.

### Changes / Improvements

Replace this text with notes any improvements you made as a result of the testing.

![alt text](screenshots/sprint3/delete-image-fix.png)

And testing this again it works correctly without removing the default profile image from the database. Talking this change through with my user they thought I should add a confirmation popup before deleting the user to prevent accidents.

![alt text](screenshots/sprint3/delete-user-fix.gif)

Going through this again with my end-user they thought the change worked well.

Maybe add something about UX/Heuristics.


## Testing Breaking In

Throughout my testing I have noticed that many of my routes and pages can easily be accessed by entering the route and bypassing any requirements.

### Changes / Improvements

I added checks to each of the relevant routes to ensure security and no errors occur, such as:

![alt text](screenshots/sprint3/creator-confirm.png)


## Sprint Review

I think that this sprint went well, I made sure that all of the functionality I intended for the web app was implemented and tested thoroughly, iterating through each part of the web app so that it worked correctly. Testing with my end-user whenever I added major pages/routes to ensure that my end-user was happy with the changes made and added any suggestions that they had for me. Some of the pages took a long time to get working properly but now the website is fully running and usable for genuine users.