# Project Requirements

## Identified Problem or Need

Rami, the owner of Chess in Nelson (I.e. The Nelson Chess club), CURRENTLY tracks his fortnightly Teams Tournaments manually using a spreadsheet (barbaric I know). At the end of each and every session, Rami works out which players have the highest points (selection of captains), note who was in which team (winning/lossing), and he updates all these by himself. This process is time consuming, could come with errors, and the system (as of currently) is of a poor grade for members to check standings themselves. I believe there is a genuine need for a web-based system to handle the Nelson Chess club, results, clients, and maybe even more if time allows.
Rami also tracks normal club meetings so that he knows who was there and who owes him for said session. 
Rami also has classes where he teaches a range of things different ages and skill levels.

## End-User Requirements

There are two types of end users: 
Rami: 
-Admin. 
-Needs to be able to quickl set up each session (who is in which team, who is said team's captain, and also which team is roating)
-Atuomatically calculate the teams, and player scores- update season standings session to session. 
-Needs to work on both phone and computer- as is run in person
(Club) members: 
-Regular users
-Regular users are only able to view teams tournament standings, sign into/upto classes, etc. 
-Regular users have ZERO login needs as they only fill out a form using personal info. 

## Proposed Solution

I propose a web-based application that will use SQL, html, and other languages, to manage Chess in Nelson's Teams Tournaments. The system will allow members to sign up for classes, and obviously see the standings. With Rami as the clear admin, He will be able to view (and review) attendace, assign team captains, input results, and should no longer have a need to manually input anything towards the standings other than the results game-to-game (who won, who lost). The db will store players, sessions, and classes. The database will store players, sessions, team assignments, game results, and seasons scores. Note; team assignments are negligable (*in the db) as teams change, only thing would be a grouping for each session. 


# Relevant Implications

## Privacy

Privacy refers to protection of personal information, ensuring that user data is only accessible to the people who are supposed to view it, and that it is stored and handled through responsible means. 

### Relevance to the System

This system will store personal information about club/class members, including their names, and emails. This makes privacy a significant concern. 

### Impact / Considerations

Passwords must be hashed, and never stored in plain text. Member data should ONLY be visible to Rami (and/or other admins if that is a want), and NOT other regular users. I will need to implement a proper handling of sessions so users can only access their own data, though I think it may also be benefitial to stalk other people standing/track record- for some friendly insight/maybe some banter. However this by no means, means that this will be a social platform. I don't need any data past basic functionality.


## Functionality

In simple words functionality means every works as intended.

### Relevance to the System

This is a tool Rami will rely on-as a replacement for his current spreadsheet-during live sessions at chess club events. If something fails mid-session (e.g. Results don't save, team shuffles/assignments don't work), it creates a real problem. AND... defeats the entire purpose of this app.

### Impact / Considerations

I will need to (contunially) thoroughly test every feature myself before handing it to Rami, and then have Rami and potentially some club members test the limits too. Things like captain selcection, players arving late (causes a conflict to the curerent possibly already running games/player setups). Things like sessions ending early will be catered for as I plan for the 'end' of a session to have to be manually selected to... end a session of course. I will fix issues based on feadback. 



## Usability

Usability means how easy and intuitive the system is as a whole. Simply put this is the measure of whether or not someone can (EASILY) pick it up and figure it out without needing instructions (Or at least not ideally having instructions)

### Relevance to the System

Rami needs to operate this system quickly during live systems (instead of after), likely on his phone. Club/class members range in age and most probably tech confidence. Members loging themselves into the site to mark their own attendance, and what not is a no no as people range in age and tech ability, it is far more optimal for Rami to do this himself. 
### Impact / Considerations

The design needs tro be simple and efficient, escpecially for session setup, and result entries. I'll show early version to Rami, and get feedback on whether the flow makes good (or any sense) to him. Mobile-friendlyiness is a must- given that Ramu confirmed that he will be (primarily at a minimum) using his phone.


## Security

Secrurity refers to protection from unauthorised access. Ensuring only legitimate users can sign in, and users can only do what their said roles allow. 

### Relevance to the System

The system has two roles: Admin (Rami), and regular users. A regular member should not be able to enter results, modify standings, and also be unable to view other members data. Without security, data could be broken by anyone who wishes it-or someone who is salty after a few lost games. 

### Impact / Considerations

The system will work through seperate roles, and role-based access. Admin-only routes will be inaccessible to normal users, passwords will be hashed, etc.


## End User

The end user implication means designing with and around the actual people who the system will be built for. The ultimate goal is to meet their expectations. 

### Relevance to the System

The two user groups have very different needs AND levels of involvement. Rami is the main power user whom needs full control; club members need a simple login and view of standing/attendances. Working thoroughly through one without much respect for the other would be pointless. 

### Impact / Considerations

I'll need to design seperate views and interfaces for admin and regular users. I will involve Rami early on and throughout testing(s) to make sure the flow matches how he runs a session, rather than how I imagine he would. For example; I see how he takes notes on which team is winning, but knowing the exact how of his tracking for individuals, and teams as a whole will need to be thoroughly investigated. 


# User Experience (UX) Principles

## Visibility of Status

In short this means the system should always keep users informed about what is happening. Feedback, status, or even indicators of teh current state.

### Relevance to the System

During a session, Rami needs to know at a glance: which players are attending, which team they're on, what the current score is, and most noteably: whether the result's have been saved. Without meeting these requirements, it could be easy for errors/mistakes to arrise.

### Impact / Considerations

I'll make sure things such as team score update visibly as results are entered, and that saving actions have a clear confirmation that all is good (likely flash messages). The CURRENT phase/state of a session should be on screen and obvious at all times (e.g. which round it is, phases, etc).

Note: a "phase" as said in Rami words, is a part of the Teams Tournaments that runs throughout the year. Each year there are two phases. Both run 6 months (ish). 

## System vs real world useage

In short, this system means that the system should use language, concepts, and structures that match how the user already thinks about the problem.

### Relevance to the System

Rami already has a mental model of how the tournament works (#NOTE# this is my understanding, update later if wrong): phases (already explained above), captains, team scores, individual(s) points. If the app uses different terminology, or structures things differently to how he natuarally thinks about it, it will be harder to use and feel kinda off.

### Impact / Considerations

I will be using language Rami is already familiar with as much as possible. There may be some formatting changes-which is to be expected with a new system-but for the most part nearly everything will be identical.


## Error Prevention

This principle means designing the system in a way that activley prevents mistakes from happening in the first place, rather than after the fact fixes (this kinda already happens as the system literally only does what it's told, but it is a convinient principle to put to use nonetheless).

### Relevance to the System

Result entries are the most error prone part of any system. Entering an incorrect score or ending a phase too early could have a heavy impact on standings. Given that sessions are live and face-paces, there isn't always time to carefully double-check everything.

### Impact / Considerations

I'll add some sort of confirmation check only for irreversible actions like ending a phase-though, I AM highly likely to add some way of editing these later on. Input feilds for scores should be permitted only valid values (i.e. points per result being: Loss; 0, Draw; 0.5, Win; 1).
Where possible the system should warn Rami IF something is off (more or less noting errors), such as not all games being submitted before ending a session. Though I'm sure this kind of thing is just decorative as Rami has been doing these types of error checks on his own for quite a while.

