Team Pulse
==============

Purpose:
--------------
The purpose of the *Team Health Score* project is to collect employee ratings of four happiness criteria. These ratings are then used to measure employee satisfaction and overall project health. Aggregate values are calculated and graphically displayed in order to give Modeans a view into how project health has changed overtime.   

Improvements:
--------------
Team Pulse is an improved version of the original team health score app in use at Modea for measuring employee satisfaction. Team Pulse is an improvement over the old team health score in the following ways.
 * it's more flexible - we have more control over what the app does, how it performs, and how it looks
 * it's more automatic - less work for Courtney and me to do on a weekly basis
 * it's sustainable - I won't have to update scripts on a weekly basis to get visualizations to work

Components:
--------------
 * Google App Engine 1.7.5
 * App Engine DataStore
 * Python 2.7
 * webapp2 (restful wsgi framework)
 * jinja2 (templates)
 * Google Visualization Javascript library 
 * Google Apps Atom API

Features:
--------------
 * entry form for collecting employee satisfaction info and storing it in the App Engine DataStore
 * ability to import data from google docs into Pulse Google datastore instance(s)
all Team Health visualization pages from the old app:
    * summary visualization - displays average aggregate score for all projects with feedback for the most recent period
    * breakout visualization - displays average pride, communication, expectations, and challenge ratings for th most recent period
    * project visualizations - displays summary stats for each active project
administration site section which allows anyone with access to add/remove users and projects, and remove score records
 * score record tables with restricted access

Rating Categories
--------------
The 4 rating categories are defined accordingly.
 * Pride - I'm proud of the work my team has done in the past week
 * Expectations - The expectations placed on me in the past week have been fair
 * Challenge - During the past week I have felt challenged while working on this project
 * Communication - I have received timely and effective communication from my team in the past week
