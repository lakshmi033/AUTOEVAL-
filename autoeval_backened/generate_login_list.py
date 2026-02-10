
def generate_list():
    student_names = [
        "James Smith", "Maria Garcia", "Robert Johnson", "Lisa Rodriguez", "Michael Williams", 
        "Sarah Martinez", "William Brown", "Kimberly Davis", "David Jones", "Jennifer Lopez",
        "Richard Miller", "Susan Wilson", "Joseph Moore", "Karen Taylor", "Thomas Anderson", 
        "Nancy Thomas", "Charles Jackson", "Margaret White", "Christopher Harris", "Betty Martin",
        "Daniel Thompson", "Sandra Clark", "Matthew Robinson", "Ashley Lewis", "Anthony Lee", 
        "Dorothy Walker", "Mark Hall", "Kimberly Allen", "Donald Young", "Donna Hernandez",
        "Steven King", "Emily Wright", "Paul Lopez", "Carol Hill", "Andrew Scott", 
        "Michelle Green", "Joshua Adams", "Amanda Baker", "Kenneth Gonzalez", "Melissa Nelson",
        "Kevin Carter", "Deborah Mitchell", "Brian Perez", "Stephanie Roberts", "George Turner", 
        "Rebecca Phillips", "Edward Campbell", "Sharon Parker", "Ronald Evans", "Laura Edwards",
        "Timothy Collins", "Cynthia Stewart", "Jason Sanchez", "Kathleen Morris", "Jeffrey Rogers", 
        "Amy Reed", "Ryan Cook", "Shirley Morgan", "Jacob Bell", "Angela Murphy",
        "Gary Bailey", "Helen Rivera", "Nicholas Cooper", "Anna Richardson", "Eric Cox", 
        "Brenda Howard", "Stephen Ward", "Pamela Torres", "Jonathan Peterson", "Nicole Gray",
        "Larry Ramirez", "Samantha James", "Justin Watson", "Katherine Brooks", "Scott Kelly", 
        "Christine Sanders", "Frank Price", "Debra Bennett", "Brandon Wood", "Rachel Barnes",
        "Raymond Ross", "Carolyn Henderson", "Gregory Coleman", "Janet Jenkins", "Benjamin Perry", 
        "Maria Powell", "Samuel Long", "Heather Patterson", "Patrick Hughes", "Diane Flores"
    ]
    
    with open("all_student_logins.md", "w") as f:
        f.write("# Full Student Login List (90 Users)\n\n")
        f.write("**Use these credentials to log in as a student.**\n")
        f.write("**Default Password for EVERYONE:** `student123`\n\n")
        f.write("| No. | Name | Email (Login ID) | Password |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        # Track used emails to match rebuild_db logic exactly (though list is unique)
        used_emails = set()
        
        for idx, full_name in enumerate(student_names):
            name_parts = full_name.lower().split()
            if len(name_parts) >= 2:
                email_prefix = f"{name_parts[0]}.{name_parts[-1]}"
            else:
                email_prefix = name_parts[0]
            
            email = f"{email_prefix}@school.com"
            
            # Simple collision handling (rebuild_db style roughly)
            if email in used_emails:
                 email = f"{email_prefix}{idx}@school.com"
            used_emails.add(email)
            
            f.write(f"| {idx+1} | {full_name} | `{email}` | `student123` |\n")

if __name__ == "__main__":
    generate_list()
    print("List generated successfully.")
