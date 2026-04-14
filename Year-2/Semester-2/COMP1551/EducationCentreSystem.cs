// ============================================================
// COMP1551 Application Development - Coursework
// Module Leader: Tuan Nguyen
// Student Name: The Viet Phan
// Student ID: GCS240020
// ============================================================
// Project:  Education Centre Desktop Information System
// Language: C# Console Application
// OOP Principles Demonstrated:
//   - Encapsulation  : private fields with public properties
//   - Inheritance    : Teacher, Admin, Student extend Person
//   - Polymorphism   : virtual/override Display() and Edit()
// ============================================================

using System;
using System.Collections.Generic;

// ============================================================
// BASE CLASS: Person
// ============================================================
// Person is declared abstract so it cannot be instantiated
// directly - only its derived classes (Teacher, Admin, Student)
// can be created. It holds the four fields that every user type
// shares and declares the abstract contract (Edit) that all
// derived classes must fulfil.
// ============================================================
abstract class Person
{
    // --------------------------------------------------------
    // Private backing fields - encapsulation ensures these
    // cannot be modified directly from outside the class.
    // All access goes through the public properties below.
    // --------------------------------------------------------
    private string name;
    private string telephone;
    private string email;
    private string role;

    // --------------------------------------------------------
    // Constructor
    // Called by every derived class constructor via base(...).
    // Assigns values to all shared fields in one place so that
    // derived classes do not repeat this initialisation logic.
    // --------------------------------------------------------
    public Person(string name, string telephone, string email, string role)
    {
        this.name      = name;
        this.telephone = telephone;
        this.email     = email;
        this.role      = role;
    }

    // --------------------------------------------------------
    // Properties (Encapsulation)
    // Each property wraps a private field with a getter and a
    // setter, giving callers controlled access.
    // --------------------------------------------------------

    // Name - full name of the person
    public string Name
    {
        get { return name; }
        set { name = value; }
    }

    // Telephone - contact phone number
    public string Telephone
    {
        get { return telephone; }
        set { telephone = value; }
    }

    // Email - contact email address
    public string Email
    {
        get { return email; }
        set { email = value; }
    }

    // Role - read publicly, but only settable by derived classes
    // (protected set), so external code cannot change the role
    // of an existing object after it has been created.
    public string Role
    {
        get { return role; }
        protected set { role = value; }
    }

    // --------------------------------------------------------
    // Virtual Display() - Polymorphism
    // Prints the four shared fields to the console.
    // Marked virtual so derived classes can override it and
    // call base.Display() to reuse this implementation before
    // printing their own additional fields.
    // --------------------------------------------------------
    public virtual void Display()
    {
        Console.WriteLine($"  Name:      {name}");
        Console.WriteLine($"  Telephone: {telephone}");
        Console.WriteLine($"  Email:     {email}");
        Console.WriteLine($"  Role:      {role}");
    }

    // --------------------------------------------------------
    // Abstract Edit() - Polymorphism + Inheritance contract
    // Declared abstract (no body here) so every derived class
    // is forced to provide its own implementation. This allows
    // the Program class to call Edit() on any Person reference
    // and have the correct version execute at runtime.
    // --------------------------------------------------------
    public abstract void Edit();
}

// ============================================================
// DERIVED CLASS: Teacher
// ============================================================
// Teacher inherits all shared fields and behaviour from Person
// and adds three fields specific to teaching staff:
//   salary    - annual salary in pounds
//   subject1  - name of first subject taught
//   subject2  - name of second subject taught
// ============================================================
class Teacher : Person
{
    // Private fields specific to the Teacher class.
    // Accessible only through the properties defined below.
    private double salary;
    private string subject1;
    private string subject2;

    // --------------------------------------------------------
    // Constructor
    // Passes the shared parameters to Person via base(...),
    // hard-coding the role string as "Teacher". Then
    // initialises the three teacher-specific fields.
    // --------------------------------------------------------
    public Teacher(string name, string telephone, string email,
                   double salary, string subject1, string subject2)
        : base(name, telephone, email, "Teacher")
    {
        this.salary   = salary;
        this.subject1 = subject1;
        this.subject2 = subject2;
    }

    // --------------------------------------------------------
    // Properties - encapsulated access to private fields
    // --------------------------------------------------------

    // Annual salary in pounds sterling
    public double Salary
    {
        get { return salary; }
        set { salary = value; }
    }

    // Name of the first subject taught by this teacher
    public string Subject1
    {
        get { return subject1; }
        set { subject1 = value; }
    }

    // Name of the second subject taught by this teacher
    public string Subject2
    {
        get { return subject2; }
        set { subject2 = value; }
    }

    // --------------------------------------------------------
    // Override Display() - Polymorphism
    // Calls the base implementation first (prints Name,
    // Telephone, Email, Role) then appends the three fields
    // that are unique to teachers.
    // --------------------------------------------------------
    public override void Display()
    {
        base.Display();  // Print the four shared fields first
        Console.WriteLine($"  Salary:    £{salary:F2}");
        Console.WriteLine($"  Subject 1: {subject1}");
        Console.WriteLine($"  Subject 2: {subject2}");
    }

    // --------------------------------------------------------
    // Override Edit() - Polymorphism
    // Prompts the user to update every field belonging to this
    // teacher record. Pressing Enter (blank input) leaves the
    // existing value unchanged. Salary input is validated with
    // TryParse so non-numeric input is safely ignored.
    // --------------------------------------------------------
    public override void Edit()
    {
        // Prompt for each shared field (inherited from Person)
        Console.Write($"  Name [{Name}]: ");
        string input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Name = input;

        Console.Write($"  Telephone [{Telephone}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Telephone = input;

        Console.Write($"  Email [{Email}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Email = input;

        // Salary: only update if the user enters a valid number
        Console.Write($"  Salary [{salary}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input) && double.TryParse(input, out double sal))
            salary = sal;

        // Prompt for the two teacher-specific subject fields
        Console.Write($"  Subject 1 [{subject1}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) subject1 = input;

        Console.Write($"  Subject 2 [{subject2}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) subject2 = input;
    }
}

// ============================================================
// DERIVED CLASS: Admin
// ============================================================
// Admin inherits all shared fields from Person and adds three
// fields specific to administration staff:
//   salary       - annual salary in pounds
//   isFullTime   - true = full-time; false = part-time
//   workingHours - contracted hours per week
// ============================================================
class Admin : Person
{
    // Private fields specific to administration staff.
    private double salary;
    private bool   isFullTime;
    private double workingHours;

    // --------------------------------------------------------
    // Constructor
    // Delegates the four shared fields to base Person and
    // sets the role string to "Admin". Initialises the three
    // admin-specific fields from the supplied arguments.
    // --------------------------------------------------------
    public Admin(string name, string telephone, string email,
                 double salary, bool isFullTime, double workingHours)
        : base(name, telephone, email, "Admin")
    {
        this.salary       = salary;
        this.isFullTime   = isFullTime;
        this.workingHours = workingHours;
    }

    // --------------------------------------------------------
    // Properties - encapsulated access to private fields
    // --------------------------------------------------------

    // Annual salary in pounds sterling
    public double Salary
    {
        get { return salary; }
        set { salary = value; }
    }

    // Employment type: true = full-time, false = part-time
    public bool IsFullTime
    {
        get { return isFullTime; }
        set { isFullTime = value; }
    }

    // Number of contracted hours worked per week
    public double WorkingHours
    {
        get { return workingHours; }
        set { workingHours = value; }
    }

    // --------------------------------------------------------
    // Override Display() - Polymorphism
    // Calls base.Display() for shared fields then prints the
    // three administration-specific fields. The boolean
    // isFullTime is shown as a human-readable "Full-time" or
    // "Part-time" string using a conditional expression.
    // --------------------------------------------------------
    public override void Display()
    {
        base.Display();  // Print the four shared fields first
        Console.WriteLine($"  Salary:        £{salary:F2}");
        Console.WriteLine($"  Employment:    {(isFullTime ? "Full-time" : "Part-time")}");
        Console.WriteLine($"  Working Hours: {workingHours} hrs/week");
    }

    // --------------------------------------------------------
    // Override Edit() - Polymorphism
    // Prompts for all admin fields. The boolean isFullTime is
    // collected via a y/n prompt; any other input leaves the
    // current value unchanged.
    // --------------------------------------------------------
    public override void Edit()
    {
        // Prompt for the four shared Person fields
        Console.Write($"  Name [{Name}]: ");
        string input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Name = input;

        Console.Write($"  Telephone [{Telephone}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Telephone = input;

        Console.Write($"  Email [{Email}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Email = input;

        // Salary: only update if the user provides a valid number
        Console.Write($"  Salary [{salary}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input) && double.TryParse(input, out double sal))
            salary = sal;

        // Employment type: accept 'y' (full-time) or 'n' (part-time)
        // Current value is displayed so the user knows what is stored.
        Console.Write($"  Full-time? (y/n) [{(isFullTime ? "y" : "n")}]: ");
        input = Console.ReadLine()?.ToLower();
        if      (input == "y") isFullTime = true;
        else if (input == "n") isFullTime = false;

        // Working hours: only update if a valid number is entered
        Console.Write($"  Working Hours [{workingHours}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input) && double.TryParse(input, out double hrs))
            workingHours = hrs;
    }
}

// ============================================================
// DERIVED CLASS: Student
// ============================================================
// Student inherits all shared fields from Person and adds
// three enrolled subject names. Students have no salary or
// employment data, distinguishing them clearly from staff.
// ============================================================
class Student : Person
{
    // Private fields holding the three enrolled subject names.
    private string subject1;
    private string subject2;
    private string subject3;

    // --------------------------------------------------------
    // Constructor
    // Passes shared fields to base Person with the role set
    // to "Student". Stores the three subject name arguments.
    // --------------------------------------------------------
    public Student(string name, string telephone, string email,
                   string subject1, string subject2, string subject3)
        : base(name, telephone, email, "Student")
    {
        this.subject1 = subject1;
        this.subject2 = subject2;
        this.subject3 = subject3;
    }

    // --------------------------------------------------------
    // Properties - encapsulated access to private subject fields
    // --------------------------------------------------------

    // Name of the student's first enrolled subject
    public string Subject1
    {
        get { return subject1; }
        set { subject1 = value; }
    }

    // Name of the student's second enrolled subject
    public string Subject2
    {
        get { return subject2; }
        set { subject2 = value; }
    }

    // Name of the student's third enrolled subject
    public string Subject3
    {
        get { return subject3; }
        set { subject3 = value; }
    }

    // --------------------------------------------------------
    // Override Display() - Polymorphism
    // Calls base.Display() to print shared fields then appends
    // the three subject names specific to this student.
    // --------------------------------------------------------
    public override void Display()
    {
        base.Display();  // Print the four shared fields first
        Console.WriteLine($"  Subject 1: {subject1}");
        Console.WriteLine($"  Subject 2: {subject2}");
        Console.WriteLine($"  Subject 3: {subject3}");
    }

    // --------------------------------------------------------
    // Override Edit() - Polymorphism
    // Prompts for all student fields. Blank input retains the
    // currently stored value for any field.
    // --------------------------------------------------------
    public override void Edit()
    {
        // Prompt for the four shared Person fields
        Console.Write($"  Name [{Name}]: ");
        string input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Name = input;

        Console.Write($"  Telephone [{Telephone}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Telephone = input;

        Console.Write($"  Email [{Email}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) Email = input;

        // Prompt for the three student-specific subject fields
        Console.Write($"  Subject 1 [{subject1}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) subject1 = input;

        Console.Write($"  Subject 2 [{subject2}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) subject2 = input;

        Console.Write($"  Subject 3 [{subject3}]: ");
        input = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(input)) subject3 = input;
    }
}

// ============================================================
// MAIN PROGRAM CLASS
// ============================================================
// Contains the application entry point and all menu-driven
// operations. Uses a single static List<Person> as the data
// structure for all records.
//
// Because List<Person> holds references to the base type, it
// can store Teacher, Admin, and Student objects together.
// When Display() or Edit() is called on a list element, the
// runtime resolves the correct override automatically - this
// is runtime polymorphism (dynamic dispatch).
// ============================================================
class Program
{
    // --------------------------------------------------------
    // people - the central dynamic data structure.
    // List<Person> expands automatically as records are added,
    // so it can hold an unlimited number of objects. Declared
    // static because all menu methods share the same list
    // without needing to pass it as a parameter.
    // --------------------------------------------------------
    static List<Person> people = new List<Person>();

    // --------------------------------------------------------
    // Main - application entry point
    // Sets the console title, seeds sample data so the system
    // is demonstrable on first launch, then enters the main
    // menu loop. The loop runs until the user chooses Exit (6).
    // --------------------------------------------------------
    static void Main(string[] args)
    {
        // Set a descriptive window title for the console
        Console.Title = "Education Centre Desktop Information System";

        // Populate the list with representative sample records
        SeedData();

        // Keep displaying the menu until the user exits
        bool running = true;
        while (running)
        {
            // Render the menu and read the user's selection
            ShowMainMenu();
            string choice = Console.ReadLine()?.Trim();

            // Route each numeric choice to the matching method
            switch (choice)
            {
                case "1": AddRecord();      break;  // Add a new person record
                case "2": ViewAllRecords(); break;  // Show every record
                case "3": ViewByRole();     break;  // Filter records by role
                case "4": EditRecord();     break;  // Modify an existing record
                case "5": DeleteRecord();   break;  // Remove a record
                case "6": running = false;  break;  // Exit the application
                default:
                    // Handle any input that does not match a valid option
                    Console.WriteLine("\n  Invalid option. Press Enter to continue.");
                    Console.ReadLine();
                    break;
            }
        }

        // Farewell message displayed before the application closes
        Console.WriteLine("\n  Goodbye.");
    }

    // --------------------------------------------------------
    // ShowMainMenu
    // Clears the screen and prints the numbered main menu.
    // Called at the start of every loop iteration so the user
    // always sees a clean menu after completing an operation.
    // --------------------------------------------------------
    static void ShowMainMenu()
    {
        Console.Clear();
        Console.WriteLine("==========================================");
        Console.WriteLine("  Education Centre Information System");
        Console.WriteLine("==========================================");
        Console.WriteLine("  1. Add New Record");
        Console.WriteLine("  2. View All Records");
        Console.WriteLine("  3. View Records by Role");
        Console.WriteLine("  4. Edit Existing Record");
        Console.WriteLine("  5. Delete Record");
        Console.WriteLine("  6. Exit");
        Console.WriteLine("==========================================");
        Console.Write("  Select an option: ");
    }

    // --------------------------------------------------------
    // AddRecord
    // Prompts the user to select a role (Teacher / Admin /
    // Student) then collects the required fields for that role.
    // Shared fields (Name, Telephone, Email) are collected
    // first, followed by the role-specific fields. A new object
    // of the appropriate derived class is then created and
    // appended to the people list.
    // --------------------------------------------------------
    static void AddRecord()
    {
        Console.Clear();
        Console.WriteLine("==========================================");
        Console.WriteLine("  Add New Record");
        Console.WriteLine("==========================================");

        // Ask the user to choose which role to add
        Console.WriteLine("  Select role:");
        Console.WriteLine("  1. Teacher");
        Console.WriteLine("  2. Admin");
        Console.WriteLine("  3. Student");
        Console.Write("  Choice: ");
        string roleChoice = Console.ReadLine()?.Trim();

        // Collect the four fields shared by all person types
        Console.Write("  Name: ");
        string name = Console.ReadLine();

        Console.Write("  Telephone: ");
        string telephone = Console.ReadLine();

        Console.Write("  Email: ");
        string email = Console.ReadLine();

        // Branch based on the chosen role to collect role-specific
        // data and create the correct derived class object.
        switch (roleChoice)
        {
            case "1":
                // --- Teacher-specific fields ---
                Console.Write("  Salary: £");
                // TryParse prevents a crash if the user enters non-numeric text
                double.TryParse(Console.ReadLine(), out double tSalary);

                Console.Write("  Subject 1: ");
                string ts1 = Console.ReadLine();

                Console.Write("  Subject 2: ");
                string ts2 = Console.ReadLine();

                // Instantiate a Teacher and add it to the shared list
                people.Add(new Teacher(name, telephone, email, tSalary, ts1, ts2));
                break;

            case "2":
                // --- Admin-specific fields ---
                Console.Write("  Salary: £");
                double.TryParse(Console.ReadLine(), out double aSalary);

                // Employment type is collected as a y/n character
                Console.Write("  Full-time? (y/n): ");
                bool fullTime = Console.ReadLine()?.ToLower() == "y";

                Console.Write("  Working Hours per week: ");
                double.TryParse(Console.ReadLine(), out double hours);

                // Instantiate an Admin and add it to the shared list
                people.Add(new Admin(name, telephone, email, aSalary, fullTime, hours));
                break;

            case "3":
                // --- Student-specific fields ---
                Console.Write("  Subject 1: ");
                string ss1 = Console.ReadLine();

                Console.Write("  Subject 2: ");
                string ss2 = Console.ReadLine();

                Console.Write("  Subject 3: ");
                string ss3 = Console.ReadLine();

                // Instantiate a Student and add it to the shared list
                people.Add(new Student(name, telephone, email, ss1, ss2, ss3));
                break;

            default:
                // Inform the user if their role selection was not recognised
                Console.WriteLine("\n  Invalid role selection. Record not added.");
                Console.ReadLine();
                return;
        }

        Console.WriteLine("\n  Record added successfully. Press Enter to continue.");
        Console.ReadLine();
    }

    // --------------------------------------------------------
    // ViewAllRecords
    // Iterates through every element in the people list and
    // calls Display() on each one. Because people is typed as
    // List<Person> but contains Teacher, Admin, and Student
    // objects, the runtime invokes the correct overridden
    // Display() method for each element (polymorphism).
    // --------------------------------------------------------
    static void ViewAllRecords()
    {
        Console.Clear();
        Console.WriteLine("==========================================");
        Console.WriteLine("  All Records");
        Console.WriteLine("==========================================");

        // Inform the user if there are currently no records stored
        if (people.Count == 0)
        {
            Console.WriteLine("  No records found.");
        }
        else
        {
            // Display each record with a numbered heading for readability
            for (int i = 0; i < people.Count; i++)
            {
                Console.WriteLine($"\n  [{i + 1}] ----------------------------------------");
                // Polymorphic call: Display() resolves to Teacher, Admin, or Student
                people[i].Display();
            }
        }

        Console.WriteLine("\n  Press Enter to continue.");
        Console.ReadLine();
    }

    // --------------------------------------------------------
    // ViewByRole
    // Asks the user to choose a role then iterates the list,
    // printing only those records whose Role property matches
    // the selection. Uses a switch expression to map the
    // numeric menu choice to the role string.
    // --------------------------------------------------------
    static void ViewByRole()
    {
        Console.Clear();
        Console.WriteLine("==========================================");
        Console.WriteLine("  View Records by Role");
        Console.WriteLine("==========================================");
        Console.WriteLine("  1. Teachers");
        Console.WriteLine("  2. Admin Staff");
        Console.WriteLine("  3. Students");
        Console.Write("  Choice: ");
        string choice = Console.ReadLine()?.Trim();

        // Translate the numeric choice into the role string
        // used in Person.Role so records can be matched.
        string roleFilter = choice switch
        {
            "1" => "Teacher",
            "2" => "Admin",
            "3" => "Student",
            _   => ""          // Empty string signals an unrecognised choice
        };

        // Reject any input that did not match a valid option
        if (string.IsNullOrEmpty(roleFilter))
        {
            Console.WriteLine("\n  Invalid selection. Press Enter to continue.");
            Console.ReadLine();
            return;
        }

        Console.WriteLine($"\n  --- {roleFilter} Records ---");
        bool found = false;  // Track whether any matching records were found

        // Iterate all records and display only those matching the chosen role
        foreach (Person p in people)
        {
            if (p.Role == roleFilter)
            {
                Console.WriteLine("\n  ----------------------------------------");
                p.Display();   // Polymorphic call to the correct override
                found = true;
            }
        }

        // Inform the user if no records exist for the selected role
        if (!found)
            Console.WriteLine($"\n  No {roleFilter} records found.");

        Console.WriteLine("\n  Press Enter to continue.");
        Console.ReadLine();
    }

    // --------------------------------------------------------
    // EditRecord
    // Displays a numbered summary of all records so the user
    // can identify which one to edit. After the user enters a
    // valid record number, the polymorphic Edit() method is
    // called on that Person object - Teacher.Edit(), Admin.Edit()
    // or Student.Edit() is invoked automatically at runtime.
    // --------------------------------------------------------
    static void EditRecord()
    {
        Console.Clear();
        Console.WriteLine("==========================================");
        Console.WriteLine("  Edit Record");
        Console.WriteLine("==========================================");

        // Cannot edit if there are no records in the list
        if (people.Count == 0)
        {
            Console.WriteLine("  No records available to edit. Press Enter to continue.");
            Console.ReadLine();
            return;
        }

        // Print a concise numbered list (Name + Role) for record selection
        for (int i = 0; i < people.Count; i++)
            Console.WriteLine($"  [{i + 1}] {people[i].Name} ({people[i].Role})");

        // Read and validate the user's choice
        Console.Write("\n  Enter record number to edit: ");
        if (!int.TryParse(Console.ReadLine(), out int index) || index < 1 || index > people.Count)
        {
            Console.WriteLine("  Invalid selection. Press Enter to continue.");
            Console.ReadLine();
            return;
        }

        // Remind the user they can skip fields by pressing Enter
        Console.WriteLine("\n  Leave any field blank to keep the existing value.\n");

        // Polymorphic dispatch: calls the Edit() override matching the
        // actual runtime type of the selected Person object.
        people[index - 1].Edit();

        Console.WriteLine("\n  Record updated successfully. Press Enter to continue.");
        Console.ReadLine();
    }

    // --------------------------------------------------------
    // DeleteRecord
    // Displays a numbered summary of all records, validates the
    // user's selection, asks for explicit confirmation, then
    // removes the chosen record from the list. Confirmation
    // prevents accidental permanent deletion of data.
    // --------------------------------------------------------
    static void DeleteRecord()
    {
        Console.Clear();
        Console.WriteLine("==========================================");
        Console.WriteLine("  Delete Record");
        Console.WriteLine("==========================================");

        // Cannot delete if there are no records in the list
        if (people.Count == 0)
        {
            Console.WriteLine("  No records available to delete. Press Enter to continue.");
            Console.ReadLine();
            return;
        }

        // Print a numbered list so the user can identify the target record
        for (int i = 0; i < people.Count; i++)
            Console.WriteLine($"  [{i + 1}] {people[i].Name} ({people[i].Role})");

        // Read and validate the record number
        Console.Write("\n  Enter record number to delete: ");
        if (!int.TryParse(Console.ReadLine(), out int index) || index < 1 || index > people.Count)
        {
            Console.WriteLine("  Invalid selection. Press Enter to continue.");
            Console.ReadLine();
            return;
        }

        // Store a reference to the target record before removing it
        // so its name and role can be shown in the confirmation prompt.
        Person target = people[index - 1];

        // Confirm deletion with the user to prevent accidental data loss
        Console.Write($"\n  Are you sure you want to delete '{target.Name}' ({target.Role})? (y/n): ");

        if (Console.ReadLine()?.ToLower() == "y")
        {
            // RemoveAt removes the element at the given zero-based index
            people.RemoveAt(index - 1);
            Console.WriteLine("  Record deleted successfully.");
        }
        else
        {
            // User chose not to proceed - leave the list unchanged
            Console.WriteLine("  Deletion cancelled.");
        }

        Console.WriteLine("  Press Enter to continue.");
        Console.ReadLine();
    }

    // --------------------------------------------------------
    // SeedData
    // Pre-populates the list with six representative records
    // (two of each type) so the application can be demonstrated
    // immediately after launch without manually adding records.
    // Demonstrates all three derived class constructors.
    // --------------------------------------------------------
    static void SeedData()
    {
        // Add two Teacher records with salary and subject data
        people.Add(new Teacher("Dr. Sarah Johnson", "07700900123", "s.johnson@edu.ac.uk",
                               45000, "Mathematics", "Physics"));
        people.Add(new Teacher("Mr. James Lee", "07700900456", "j.lee@edu.ac.uk",
                               38000, "English", "History"));

        // Add two Admin records: one full-time (37.5 hrs) and one part-time (20 hrs)
        people.Add(new Admin("Ms. Claire Adams", "07700900789", "c.adams@edu.ac.uk",
                             28000, true, 37.5));
        people.Add(new Admin("Mr. Tom Brown", "07700901000", "t.brown@edu.ac.uk",
                             14000, false, 20.0));

        // Add two Student records each with three enrolled subjects
        people.Add(new Student("Alice Green", "07700901234", "a.green@student.edu.ac.uk",
                               "Mathematics", "Physics", "Computer Science"));
        people.Add(new Student("Bob White", "07700901567", "b.white@student.edu.ac.uk",
                               "English", "History", "Art"));
    }
}
