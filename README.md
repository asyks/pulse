Team Pulse
==============

Purpose:
--------------
The purpose of *Team Pulse* is to collect team member feedback on specific projects. This feedback is then used to measure employee satisfaction and overall project health. Summary stats are calculated and displayed graphically in order to give team members a view into how project health has changed overtime.   

Improvements:
--------------
Team Pulse is an improved version of the original team health score app in use at Modea for measuring employee satisfaction. Team Pulse is an improvement over the old team health score in the following ways:
 * it's flexible - control over what the app does, how it performs, and how it looks
 * it's automatic - user friendly interfaces for managing scores, projects, and user access
 * it's sustainable - visualization scripts will no longer need to be updated on a weekly basis

Components:
--------------
 * Google App Engine 1.7.5
 * App Engine DataStore
 * Python 2.7
 * webapp2 (restful wsgi framework)
 * jinja2 (html templates)
 * Google Visualization Javascript library 
 * Google Apps Atom API

Features:
--------------
The most notable features are:
 * entry form for collecting employee satisfaction info and storing it in the App Engine DataStore
 * data can be imported from google docs into the App Engine datastore
 * visualization pages:
    * summary visualization - displays average aggregate score for all projects with feedback for the most recent period
    * breakout visualization - displays average pride, communication, expectations, and challenge ratings for th most recent period
    * project visualizations - displays summary stats for each active project
 * administration interface for managing scores, projects, and users
 * score record tables with restricted access

Rating Categories
--------------
The 4 rating categories are defined accordingly:
 * Pride - I'm proud of the work my team has created 
 * Communication - I have received timely and effective communication from my team
 * Passion - I feel our team has been excited about this project
 * Challenge - I have felt challenged while working on this project

Users rate each project their working on based on these criteria each week

Access Levels
--------------
Basic Access allows users to:
 * submit responses
 * view visualization pages
Table Access enables users to additionally view:
 * record tables without usernames
Admin Access (full access)  enables users to additionally view and interact with:
 * record tables without usernames
 * record tables with usernames
 * project add/remove
 * special user management

UI Structure
--------------
The restricted access site section consists of the following:
 * Manage Projects - An interface for adding or removing projects, restricted to users with admin level access.
 * Manage Users - interface for adding and removing special users, and changing special users level of access, restricted to users with admin level access.
 * View All Data - A table containing all Team Pulse entries in descending order with the newest entry on top, restricted to users with table level access.
 * View Client Data - Tables for viewing responses for a single client, restricted to users with table level access.
 * Survey Comments - Tables for viewing responses with comments for a single client, restricted to users with table level access.
 * User Responses - tables for viewing responses with comments and usernames for a single client, restricted to users with admin level access.

The main (unrestricted) site section consists of the following:
 * Start Survey - An interface for submitting a response about one or more projects.
 * Results Summary - A Visualization with gauges displaying the average pulse of each project for the previous period.
 * Results Details - A Visualization with gauges displaying the average pulse, pride, communication, expectations, and challenge of each project for the previous period.
 * Client Results - A set of visualizations with gauges and line charts displaying the average pulse, pride, communication, expectations, and challenge for the previous period and the period preceding it, and a line chart displaying the historical average pulse over time for a single client.
