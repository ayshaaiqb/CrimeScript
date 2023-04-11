******
#CRIME SCRIPT FLASK WEB APPLICATION
******
This application educates users on what crime scripting is and the impact of creating one.  
  
Users can create their own scripts, view a library of other users crime scripts as well as have templates aiding them.  
  
[See Crimescript Homepage](crimescript.png)
******
#Setting up the environment
******


-Create a directory  
-Make and activate python virtual env:     
  [python -m venv virt]    
  [source virt/Scripts/activate]    
-Pip install flask    
-Pip install ALL imports from **requirements.txt**  
-Flask env setup  
  [export FLASK_DEBUG=True]  
  [export FLASK_APP=app.py]  
-Model/form setup  
	[winpty python]  
  cmd prompt:    
  [from app import app, db]  
  [app.app_context().push()]  
  [db.create_all()]    
-Migration Setup   
 [flask db init]  
 [flask db migrate -m 'Initial migration']  
 [flask db upgrade]  
