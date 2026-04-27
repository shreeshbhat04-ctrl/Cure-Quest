# This walk through on how the final project should be and the neccessary features to make it a reality
Login page
-When the user login's throught the login page like connect to google should connect him with all the services listed out
Dashboard page 
-Aside from the UI the routuine which is fed from asana should not contain everything present and the messages should be concise and a accordian type of button to view the full message 
-Routine should contain stuff like medication & routnine excersies ,remainders from calender etc
Profile card(patient)
-In the account seetting the prfile card should contain stuff like height,weight,etc etc ,prescription simulating real time patient data which can be editable
Profile card(Doctor) viewing the one
-The task clearing should redirect him to asana for reference {{{so i want to u go to tickecting.py and all the things where asana is there i want it to assign task based on doctor gid or to say which doctor thus fullfilling the task part in doctor worksapce Run this once per doctor and store in AlloyDB:
python
workspace_gid = "your_workspace_gid"
users = client.users.get_users({"workspace": workspace_gid})
for u in users:
    print(u["name"], u["gid"])

Save the GID against each doctor in your patient_doctor_map table.

---

### 5. When Creating a Task, Always Set Assignee
python
client.tasks.create_task({
    "name": f"Review care plan — {patient_name}",
    "projects": [CARE_APPROVALS_PROJECT_GID],
    "assignee": doctor_asana_user_id,   # ← this is what routes it
    "custom_fields": {
        "patient_id_field_gid": patient_id,
        "urgency_field_gid": "high"
    },
    "notes": care_plan_summary
})


---

### 6. Doctor's View — How They See Only Their Tasks
Tell each doctor to:
- Open the Care Approvals project
- Click *Filter → Assignee → Me*
- Save that as their default view and here is doctor id Workspace/Org GID: 1213916290149152

Profile/User GID: 1214276322986923     ,also make necssary changes in frontend to make this happen like removing hardcoded clear tasks to clickable or rediratble page and a feature while asking a follow up in frontend while sending or setting asaana task asking the patient which doctor and make these changes in email sending also }}}
The chat application should exist b/w the patient and Doctor
Care Maze
-the Map agent should be able to pick the user locationa and find destinations via mcp server
-also create followup and the other two buttons should be present down in the upload section for reviewing the file and chatting with user 
-The upload button is a multiple feature thing as it holdes the image_vision_agent checkout {C:\Users\shree\project\Cure-Quest\docs\image_vision_agent.md}
Meds
-The check alternative and label thing i am thinging instead of openFda ,wickipedia or anything to be replaced search on that
-Recipe agent the ui is built it should not be present or displaying the image and option all the time what should be displaying a Ui where what to take and what not take from the prescription and medication should be displayed with image,then ask agent to create recipes then the present UI should render after the recipe with customization done by the user the summary should arrive with the ingredients & quantity automattically filled by the agent and also fetch the image's of the ingrediate and reciepe generated may be by bing image and the agent should be able to fetch youttube resulst for tutorial of the recipie.
-the fallback library should be convereted to choose ur recent recipes or try new reciepes available 
-Also i am thinking of market type of thing where the ingriedents safe to consume should be available and by clicking on that the user should be redirected to amazon or something
Doctor page 
-Identify harcoded and missing endpoints in the available ui and u can plan to fix that
History
-Now the history just logs the events i want it store snapshot of the patient condition probably fetched from profile card and that so the agent can query on the diagnosis of the past and give analysis and store the data which shoud be in a accordian style button
### what u should do with this information
i want u to draft three step plan implementaion on how to proceed
-First plan: go through curequest folder and verify the the current state of the repo and identify teh missing endpoints which doesnot yet to facilate the vision of my project and make a not on what files to change in clean .md file and save in docs
-Second plan: map mentally how and what to u plan to change to what and create anything new etc etc in .md and save in docs
-Third plan:tell what do u need information from me and what i should and list that out in .md and save in docs
### execute all these sequetially as in generate one plan at a time and ask the user if he is read for next plan
### use all of ur skills availbale for this task
### medgemma strip it out the model now is gemini 3.1-flash with LLmgrounding from alloydb details on what to query from it like the tables such as indian_medicine data and the other will be given afterwards so for now strip medgemma
### agent architecture
-with the existing adk agents see if any new agents such as datafetcher ,communication,or quistioner should be created and not that having a2a protcol should be present b/w agents ,if u want to know what agent talks to what then ask me later
-Last but the least the agent should able to ask the user question like which doctor send email when to create events on calennder all that stuff like the u ask me like the ui getting rendered with options 2 options what the agents thinks it is and the other user input which the user can type get what i am trying to say 
### need any schema or getting lost on the architeture ask dont make up things 