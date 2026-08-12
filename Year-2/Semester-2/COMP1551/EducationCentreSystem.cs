// -----------------------------------------------------------------------------
// COMP1551 Application Development - Coursework, Term 2 2025/26
// Education Centre Desktop Information System
//
// Student:       Phan The Viet
// Student ID:    GCS240020
// Module leader: Tuan Nguyen
//
// A console application that replaces the paper records of an education centre.
// It holds three kinds of user - teaching staff, administration staff and
// students - and offers a menu for adding, listing, listing by role, editing
// and deleting records.
//
// The whole system is kept in this single source file, as the coursework
// requires. It is arranged top to bottom in the order it is easiest to read:
//   1. Validation      - the rules a field must satisfy
//   2. Prompt          - console input that keeps asking until a rule is met
//   3. Person          - the abstract base class
//   4. Teacher / Admin / Student - the three derived classes
//   5. PersonRegister  - the data structure holding every record
//   6. Program         - the menu and the operations behind it
// -----------------------------------------------------------------------------

using System;
using System.Collections.Generic;

// =============================================================================
// 1. VALIDATION
// =============================================================================

/// <summary>
/// The field rules of the system, gathered in one place. Both the property
/// setters and the input prompts call these methods, so a value can never be
/// accepted at the keyboard that the class itself would reject.
/// </summary>
static class Validation
{
    /// <summary>A name must contain at least one letter and no digits.</summary>
    public static bool IsName(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return false;

        bool hasLetter = false;
        foreach (char c in value)
        {
            if (char.IsDigit(c)) return false;   // "Room 12" is not a person
            if (char.IsLetter(c)) hasLetter = true;
        }
        return hasLetter;
    }

    /// <summary>
    /// A telephone number may carry a leading + and internal spaces, and must
    /// hold between seven and fifteen digits, the range allowed by E.164.
    /// </summary>
    public static bool IsTelephone(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return false;

        string trimmed = value.Trim();
        int digits = 0;

        for (int i = 0; i < trimmed.Length; i++)
        {
            char c = trimmed[i];
            if (char.IsDigit(c)) digits++;
            else if (c == '+' && i == 0) continue;      // country prefix
            else if (c == ' ' || c == '-') continue;    // grouping characters
            else return false;
        }

        return digits >= 7 && digits <= 15;
    }

    /// <summary>
    /// An email address must be of the form local@domain.tld: exactly one @,
    /// text on both sides of it, a dot in the domain and no white space.
    /// </summary>
    public static bool IsEmail(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return false;
        if (value.IndexOf(' ') >= 0) return false;

        int at = value.IndexOf('@');
        if (at <= 0) return false;                          // nothing before @
        if (at != value.LastIndexOf('@')) return false;      // more than one @

        string domain = value.Substring(at + 1);
        int dot = domain.IndexOf('.');

        // The dot must sit inside the domain, not at either end of it.
        return dot > 0 && dot < domain.Length - 1;
    }

    /// <summary>A subject name is any non-empty piece of text.</summary>
    public static bool IsSubject(string value)
    {
        return !string.IsNullOrWhiteSpace(value);
    }

    /// <summary>A salary is never negative and is capped to catch typing slips.</summary>
    public static bool IsSalary(double value)
    {
        return value >= 0 && value <= 500000;
    }

    /// <summary>Contracted hours are counted per week, so 60 is the upper limit.</summary>
    public static bool IsWorkingHours(double value)
    {
        return value > 0 && value <= 60;
    }
}

// =============================================================================
// 2. CONSOLE INPUT
// =============================================================================

/// <summary>
/// Every question the system asks at the keyboard goes through this class. Each
/// method repeats its question until the answer passes the matching rule in
/// <see cref="Validation"/>, so the calling code never has to test what it read.
///
/// Each method also takes the value currently held in the record together with
/// an "editing" flag. While a record is being entered the flag is false and an
/// answer is required; while one is being changed it is true, the stored value
/// is shown in brackets and an empty line keeps it.
/// </summary>
static class Prompt
{
    /// <summary>Reads a line, never returning null, so the caller can trim it safely.</summary>
    private static string ReadLine()
    {
        return Console.ReadLine() ?? string.Empty;
    }

    /// <summary>Writes the question, showing the current value in brackets when editing.</summary>
    private static void Ask(string label, string current, bool editing)
    {
        if (editing) Console.Write("  " + label + " [" + current + "]: ");
        else Console.Write("  " + label + ": ");
    }

    /// <summary>
    /// Asks for a piece of text. The rule to apply and the help line to show on
    /// a bad answer are both passed in, so this one loop serves every text
    /// field in the system; the four methods below name the fields it collects.
    /// </summary>
    private static string Text(string label, string current, bool editing,
                               Func<string, bool> rule, string help)
    {
        while (true)
        {
            Ask(label, current, editing);
            string answer = ReadLine().Trim();

            if (answer.Length == 0 && editing) return current;
            if (rule(answer)) return answer;

            Console.WriteLine("  " + help);
        }
    }

    /// <summary>Asks for a person's name.</summary>
    public static string Name(string label, string current, bool editing)
    {
        return Text(label, current, editing, Validation.IsName,
                    "A name must contain letters and no digits.");
    }

    /// <summary>Asks for a telephone number.</summary>
    public static string Telephone(string label, string current, bool editing)
    {
        return Text(label, current, editing, Validation.IsTelephone,
                    "Enter 7 to 15 digits, for example 020 8331 8000.");
    }

    /// <summary>Asks for an email address.</summary>
    public static string Email(string label, string current, bool editing)
    {
        return Text(label, current, editing, Validation.IsEmail,
                    "Enter an address of the form name@domain.ac.uk.");
    }

    /// <summary>Asks for the name of a subject.</summary>
    public static string Subject(string label, string current, bool editing)
    {
        return Text(label, current, editing, Validation.IsSubject,
                    "The subject name cannot be left empty.");
    }

    /// <summary>
    /// Asks for a number, working the same way as Text: one loop shared by the
    /// salary and the working hours questions, told apart by the rule passed in.
    /// </summary>
    public static double Number(string label, double current, bool editing,
                                Func<double, bool> rule, string help)
    {
        while (true)
        {
            Ask(label, current.ToString("0.##"), editing);
            string answer = ReadLine().Trim();

            if (answer.Length == 0 && editing) return current;

            double parsed;
            if (double.TryParse(answer, out parsed) && rule(parsed)) return parsed;

            Console.WriteLine("  " + help);
        }
    }

    /// <summary>Asks a yes or no question and returns true for yes.</summary>
    public static bool YesNo(string label, bool current, bool editing)
    {
        while (true)
        {
            Ask(label + " (y/n)", current ? "y" : "n", editing);
            string answer = ReadLine().Trim().ToLower();

            if (answer.Length == 0 && editing) return current;
            if (answer == "y" || answer == "yes") return true;
            if (answer == "n" || answer == "no") return false;

            Console.WriteLine("  Please answer y or n.");
        }
    }

    /// <summary>
    /// Asks for a whole number between low and high. Used for the menu itself
    /// and for choosing a record out of a numbered list.
    /// </summary>
    public static int Choice(string label, int low, int high)
    {
        while (true)
        {
            Console.Write("  " + label + ": ");
            string answer = ReadLine().Trim();

            int parsed;
            if (int.TryParse(answer, out parsed) && parsed >= low && parsed <= high)
                return parsed;

            Console.WriteLine("  Enter a number between " + low + " and " + high + ".");
        }
    }

    /// <summary>Holds the screen until the user has read what is on it.</summary>
    public static void Pause()
    {
        Console.Write("\n  Press Enter to return to the menu.");
        Console.ReadLine();
    }
}

// =============================================================================
// 3. BASE CLASS
// =============================================================================

/// <summary>
/// The data and behaviour shared by everyone the centre keeps a record of.
///
/// Person is abstract because the centre has no plain "people" on its books:
/// every record is a teacher, an administrator or a student. It therefore
/// cannot be instantiated, only inherited from.
///
/// Encapsulation: the three fields are private and are reached through
/// properties whose setters enforce the rules in <see cref="Validation"/>. A
/// Person object can never hold a blank name or a malformed email address,
/// whatever the calling code does.
/// </summary>
abstract class Person
{
    // The text fields start as empty strings: a record created by the empty
    // constructor below is filled in by CaptureDetails a moment later, and no
    // field is ever left holding nothing at all.
    private string name = string.Empty;
    private string telephone = string.Empty;
    private string email = string.Empty;

    /// <summary>
    /// Builds a record from a complete set of details. Only the derived classes
    /// can call this, through base(...), which is how the sample records are
    /// created in one statement each.
    /// </summary>
    protected Person(string name, string telephone, string email)
    {
        Name = name;              // assigned through the properties so that the
        Telephone = telephone;    // rules are applied to these values as well
        Email = email;
    }

    /// <summary>
    /// Builds an empty record, to be filled in straight away by
    /// <see cref="CaptureDetails"/>. This is the constructor the Add Record
    /// operation uses: it creates the object of the chosen type first and then
    /// asks the questions that belong to that type.
    /// </summary>
    protected Person()
    {
    }

    /// <summary>The person's full name.</summary>
    public string Name
    {
        get { return name; }
        set
        {
            if (!Validation.IsName(value))
                throw new ArgumentException("Invalid name: " + value);
            name = value;
        }
    }

    /// <summary>A contact telephone number.</summary>
    public string Telephone
    {
        get { return telephone; }
        set
        {
            if (!Validation.IsTelephone(value))
                throw new ArgumentException("Invalid telephone number: " + value);
            telephone = value;
        }
    }

    /// <summary>A contact email address.</summary>
    public string Email
    {
        get { return email; }
        set
        {
            if (!Validation.IsEmail(value))
                throw new ArgumentException("Invalid email address: " + value);
            email = value;
        }
    }

    /// <summary>
    /// The group this record belongs to. It is declared abstract and has no
    /// setter, so the role is decided by the class of the object and cannot
    /// drift out of step with it: a Teacher is a teacher for as long as it
    /// exists.
    /// </summary>
    public abstract string Role { get; }

    /// <summary>
    /// Prints the details every record has. The derived classes override this,
    /// call back into it with base.PrintDetails() and then add their own lines,
    /// so the shared block is written out once only.
    /// </summary>
    public virtual void PrintDetails()
    {
        Console.WriteLine("  Name:          " + Name);
        Console.WriteLine("  Telephone:     " + Telephone);
        Console.WriteLine("  Email:         " + Email);
        Console.WriteLine("  Role:          " + Role);
    }

    /// <summary>
    /// Asks for the details every record has. The derived classes override this
    /// the same way as PrintDetails, which means adding a record and editing one
    /// run through exactly the same questions.
    /// </summary>
    /// <param name="editing">
    /// False while a new record is being entered, when every question must be
    /// answered; true while an existing record is being changed, when an empty
    /// line keeps the value already stored.
    /// </param>
    public virtual void CaptureDetails(bool editing)
    {
        Name = Prompt.Name("Name", Name, editing);
        Telephone = Prompt.Telephone("Telephone", Telephone, editing);
        Email = Prompt.Email("Email", Email, editing);
    }

    /// <summary>
    /// A one-line summary, used by the numbered lists the user picks from when
    /// editing or deleting a record.
    /// </summary>
    public override string ToString()
    {
        return Name + " (" + Role + ")";
    }
}

// =============================================================================
// 4. DERIVED CLASSES
// =============================================================================

/// <summary>
/// A member of the teaching staff: a salary and the two subjects taught, on top
/// of the details held for everyone.
/// </summary>
class Teacher : Person
{
    private double salary;
    private string subject1 = string.Empty;
    private string subject2 = string.Empty;

    /// <summary>Builds a complete teacher record.</summary>
    public Teacher(string name, string telephone, string email,
                   double salary, string subject1, string subject2)
        : base(name, telephone, email)   // the shared details are handled by Person
    {
        Salary = salary;
        Subject1 = subject1;
        Subject2 = subject2;
    }

    /// <summary>Builds an empty teacher record for the Add Record operation.</summary>
    public Teacher()
    {
    }

    /// <summary>Annual salary in pounds.</summary>
    public double Salary
    {
        get { return salary; }
        set
        {
            if (!Validation.IsSalary(value))
                throw new ArgumentException("Invalid salary: " + value);
            salary = value;
        }
    }

    /// <summary>The first of the two subjects taught.</summary>
    public string Subject1
    {
        get { return subject1; }
        set
        {
            if (!Validation.IsSubject(value))
                throw new ArgumentException("Invalid subject name.");
            subject1 = value;
        }
    }

    /// <summary>The second of the two subjects taught.</summary>
    public string Subject2
    {
        get { return subject2; }
        set
        {
            if (!Validation.IsSubject(value))
                throw new ArgumentException("Invalid subject name.");
            subject2 = value;
        }
    }

    /// <summary>Fixed by the class itself, as explained in Person.Role.</summary>
    public override string Role
    {
        get { return "Teacher"; }
    }

    /// <summary>Prints the shared details, then the three teaching fields.</summary>
    public override void PrintDetails()
    {
        base.PrintDetails();
        Console.WriteLine("  Salary (GBP):  " + salary.ToString("N2"));
        Console.WriteLine("  Subject 1:     " + subject1);
        Console.WriteLine("  Subject 2:     " + subject2);
    }

    /// <summary>Asks the shared questions, then the three teaching ones.</summary>
    public override void CaptureDetails(bool editing)
    {
        base.CaptureDetails(editing);

        Salary = Prompt.Number("Salary (GBP)", salary, editing,
                               Validation.IsSalary,
                               "Enter a salary between 0 and 500000.");
        Subject1 = Prompt.Subject("Subject 1", subject1, editing);
        Subject2 = Prompt.Subject("Subject 2", subject2, editing);
    }
}

/// <summary>
/// A member of the administration staff: a salary, whether the post is full or
/// part time, and the hours worked each week.
/// </summary>
class Admin : Person
{
    private double salary;
    private bool fullTime;
    private double workingHours;

    /// <summary>Builds a complete administration record.</summary>
    public Admin(string name, string telephone, string email,
                 double salary, bool fullTime, double workingHours)
        : base(name, telephone, email)
    {
        Salary = salary;
        FullTime = fullTime;
        WorkingHours = workingHours;
    }

    /// <summary>Builds an empty administration record for the Add Record operation.</summary>
    public Admin()
    {
    }

    /// <summary>Annual salary in pounds.</summary>
    public double Salary
    {
        get { return salary; }
        set
        {
            if (!Validation.IsSalary(value))
                throw new ArgumentException("Invalid salary: " + value);
            salary = value;
        }
    }

    /// <summary>True for a full-time post, false for a part-time one.</summary>
    public bool FullTime
    {
        get { return fullTime; }
        set { fullTime = value; }   // a boolean cannot hold an invalid value
    }

    /// <summary>Contracted hours per week.</summary>
    public double WorkingHours
    {
        get { return workingHours; }
        set
        {
            if (!Validation.IsWorkingHours(value))
                throw new ArgumentException("Invalid working hours: " + value);
            workingHours = value;
        }
    }

    /// <summary>Fixed by the class itself, as explained in Person.Role.</summary>
    public override string Role
    {
        get { return "Admin"; }
    }

    /// <summary>Prints the shared details, then the three administration fields.</summary>
    public override void PrintDetails()
    {
        base.PrintDetails();
        Console.WriteLine("  Salary (GBP):  " + salary.ToString("N2"));
        Console.WriteLine("  Contract:      " + (fullTime ? "Full-time" : "Part-time"));
        Console.WriteLine("  Weekly hours:  " + workingHours.ToString("0.##"));
    }

    /// <summary>Asks the shared questions, then the three administration ones.</summary>
    public override void CaptureDetails(bool editing)
    {
        base.CaptureDetails(editing);

        Salary = Prompt.Number("Salary (GBP)", salary, editing,
                               Validation.IsSalary,
                               "Enter a salary between 0 and 500000.");
        FullTime = Prompt.YesNo("Full-time", fullTime, editing);
        WorkingHours = Prompt.Number("Weekly hours", workingHours, editing,
                                     Validation.IsWorkingHours,
                                     "Enter the hours worked per week, up to 60.");
    }
}

/// <summary>
/// A student: the three subjects studied, on top of the details held for
/// everyone. Students carry no pay or contract data, which is the reason the
/// salary field sits in the two staff classes rather than in Person.
/// </summary>
class Student : Person
{
    private string subject1 = string.Empty;
    private string subject2 = string.Empty;
    private string subject3 = string.Empty;

    /// <summary>Builds a complete student record.</summary>
    public Student(string name, string telephone, string email,
                   string subject1, string subject2, string subject3)
        : base(name, telephone, email)
    {
        Subject1 = subject1;
        Subject2 = subject2;
        Subject3 = subject3;
    }

    /// <summary>Builds an empty student record for the Add Record operation.</summary>
    public Student()
    {
    }

    /// <summary>The first subject studied.</summary>
    public string Subject1
    {
        get { return subject1; }
        set
        {
            if (!Validation.IsSubject(value))
                throw new ArgumentException("Invalid subject name.");
            subject1 = value;
        }
    }

    /// <summary>The second subject studied.</summary>
    public string Subject2
    {
        get { return subject2; }
        set
        {
            if (!Validation.IsSubject(value))
                throw new ArgumentException("Invalid subject name.");
            subject2 = value;
        }
    }

    /// <summary>The third subject studied.</summary>
    public string Subject3
    {
        get { return subject3; }
        set
        {
            if (!Validation.IsSubject(value))
                throw new ArgumentException("Invalid subject name.");
            subject3 = value;
        }
    }

    /// <summary>Fixed by the class itself, as explained in Person.Role.</summary>
    public override string Role
    {
        get { return "Student"; }
    }

    /// <summary>Prints the shared details, then the three subjects.</summary>
    public override void PrintDetails()
    {
        base.PrintDetails();
        Console.WriteLine("  Subject 1:     " + subject1);
        Console.WriteLine("  Subject 2:     " + subject2);
        Console.WriteLine("  Subject 3:     " + subject3);
    }

    /// <summary>Asks the shared questions, then the three subject ones.</summary>
    public override void CaptureDetails(bool editing)
    {
        base.CaptureDetails(editing);

        Subject1 = Prompt.Subject("Subject 1", subject1, editing);
        Subject2 = Prompt.Subject("Subject 2", subject2, editing);
        Subject3 = Prompt.Subject("Subject 3", subject3, editing);
    }
}

// =============================================================================
// 5. DATA STRUCTURE
// =============================================================================

/// <summary>
/// The store of records, and the only part of the system that knows how they
/// are held.
///
/// A List&lt;Person&gt; is used rather than an array because the centre cannot say in
/// advance how many records it will keep: the list grows as records are added
/// and closes the gap when one is removed. Because the list is declared on the
/// base type it holds Teacher, Admin and Student objects side by side, and the
/// operations below work on all three without asking which is which.
/// </summary>
class PersonRegister
{
    private List<Person> people = new List<Person>();

    /// <summary>How many records are currently held.</summary>
    public int Count
    {
        get { return people.Count; }
    }

    /// <summary>Reads the record at a position in the list, counting from zero.</summary>
    public Person this[int index]
    {
        get { return people[index]; }
    }

    /// <summary>Adds a record to the end of the list.</summary>
    public void Add(Person person)
    {
        people.Add(person);
    }

    /// <summary>Removes the record at the given position.</summary>
    public void RemoveAt(int index)
    {
        people.RemoveAt(index);
    }

    /// <summary>Every record, in the order they were added.</summary>
    public List<Person> All()
    {
        return people;
    }

    /// <summary>
    /// The records belonging to one group. The comparison is made against the
    /// Role property, so a record is selected by the class it was created from.
    /// </summary>
    public List<Person> ByRole(string role)
    {
        List<Person> matches = new List<Person>();

        foreach (Person person in people)
        {
            if (person.Role == role) matches.Add(person);
        }

        return matches;
    }
}

// =============================================================================
// 6. THE APPLICATION
// =============================================================================

/// <summary>
/// The menu and the five operations behind it. This class holds no data of its
/// own beyond the register; everything it prints comes from calling methods on
/// the records themselves.
/// </summary>
class Program
{
    /// <summary>The single store of records, shared by every operation below.</summary>
    private static PersonRegister register = new PersonRegister();

    /// <summary>
    /// Starts the application: loads the sample records, then shows the menu
    /// until the user chooses to close the system.
    /// </summary>
    static void Main()
    {
        LoadSampleRecords();

        bool running = true;
        while (running)
        {
            ShowMenu();

            switch (Prompt.Choice("Select an option", 1, 6))
            {
                case 1: AddRecord(); break;
                case 2: ViewAllRecords(); break;
                case 3: ViewRecordsByRole(); break;
                case 4: EditRecord(); break;
                case 5: DeleteRecord(); break;
                case 6: running = false; break;
            }
        }

        Console.WriteLine("\n  System closed.");
    }

    // -------------------------------------------------------------------------
    // Screen furniture
    // -------------------------------------------------------------------------

    /// <summary>
    /// Clears the window and writes a heading. Console.Clear throws when the
    /// output is being redirected to a file rather than to a window, so the
    /// call is skipped in that case.
    /// </summary>
    private static void Heading(string title)
    {
        if (!Console.IsOutputRedirected) Console.Clear();

        Console.WriteLine();
        Console.WriteLine("  =====================================================");
        Console.WriteLine("   " + title);
        Console.WriteLine("  =====================================================");
    }

    /// <summary>Writes the main menu.</summary>
    private static void ShowMenu()
    {
        Heading("Education Centre Information System");
        Console.WriteLine("   1. Add a new record");
        Console.WriteLine("   2. View all records");
        Console.WriteLine("   3. View records by role");
        Console.WriteLine("   4. Edit a record");
        Console.WriteLine("   5. Delete a record");
        Console.WriteLine("   6. Exit");
        Console.WriteLine("  =====================================================");
        Console.WriteLine("   Records held: " + register.Count);
        Console.WriteLine();
    }

    /// <summary>
    /// Writes a list of records, numbered from one, each set apart by a rule.
    /// PrintDetails is called on the base type, so the version belonging to the
    /// actual class of each record runs and the right fields appear. This is
    /// where polymorphism does the work: the loop never asks what it is holding.
    /// </summary>
    private static void PrintRecords(List<Person> records)
    {
        for (int i = 0; i < records.Count; i++)
        {
            Console.WriteLine("\n  [" + (i + 1) + "] -------------------------------------------------");
            records[i].PrintDetails();
        }
    }

    /// <summary>
    /// Writes a numbered one-line summary of every record and asks the user to
    /// pick one, returning its position in the register. Editing and deleting
    /// both start this way, so the code sits here rather than in either of them.
    /// </summary>
    private static int SelectRecord(string action)
    {
        Console.WriteLine();
        for (int i = 0; i < register.Count; i++)
        {
            Console.WriteLine("   " + (i + 1) + ". " + register[i]);
        }
        Console.WriteLine();

        return Prompt.Choice("Record to " + action, 1, register.Count) - 1;
    }

    // -------------------------------------------------------------------------
    // The five operations
    // -------------------------------------------------------------------------

    /// <summary>
    /// Adds a record. The user picks a group first, because that decides which
    /// class is created; the object then asks for its own fields through
    /// CaptureDetails, so this method never has to list them.
    /// </summary>
    private static void AddRecord()
    {
        Heading("Add a new record");
        Console.WriteLine("   1. Teaching staff");
        Console.WriteLine("   2. Administration");
        Console.WriteLine("   3. Student");
        Console.WriteLine();

        Person person;
        switch (Prompt.Choice("Group", 1, 3))
        {
            case 1: person = new Teacher(); break;
            case 2: person = new Admin(); break;
            default: person = new Student(); break;
        }

        Console.WriteLine();
        person.CaptureDetails(false);
        register.Add(person);

        Console.WriteLine("\n  Record saved for " + person + ".");
        Prompt.Pause();
    }

    /// <summary>Lists every record held, whichever group it belongs to.</summary>
    private static void ViewAllRecords()
    {
        Heading("All records");

        if (register.Count == 0)
        {
            Console.WriteLine("\n  There are no records to show.");
        }
        else
        {
            PrintRecords(register.All());
        }

        Prompt.Pause();
    }

    /// <summary>Lists the records of one group only.</summary>
    private static void ViewRecordsByRole()
    {
        Heading("View records by role");
        Console.WriteLine("   1. Teaching staff");
        Console.WriteLine("   2. Administration");
        Console.WriteLine("   3. Students");
        Console.WriteLine();

        // The menu numbers are turned into the role names the records carry.
        string role;
        switch (Prompt.Choice("Group", 1, 3))
        {
            case 1: role = "Teacher"; break;
            case 2: role = "Admin"; break;
            default: role = "Student"; break;
        }

        List<Person> matches = register.ByRole(role);

        if (matches.Count == 0)
        {
            Console.WriteLine("\n  There are no records in this group.");
        }
        else
        {
            Console.WriteLine("\n  " + matches.Count + " record(s) in the " + role + " group.");
            PrintRecords(matches);
        }

        Prompt.Pause();
    }

    /// <summary>
    /// Changes a record. CaptureDetails is called again, this time in editing
    /// mode, so the user is taken through the same questions with the stored
    /// values shown in brackets and an empty line keeps any of them.
    /// </summary>
    private static void EditRecord()
    {
        Heading("Edit a record");

        if (register.Count == 0)
        {
            Console.WriteLine("\n  There are no records to edit.");
            Prompt.Pause();
            return;
        }

        Person person = register[SelectRecord("edit")];

        Console.WriteLine("\n  Editing " + person + ".");
        Console.WriteLine("  Press Enter on its own to keep the value in brackets.\n");

        person.CaptureDetails(true);

        Console.WriteLine("\n  Record updated:\n");
        person.PrintDetails();
        Prompt.Pause();
    }

    /// <summary>
    /// Removes a record, after asking the user to confirm. Deletion cannot be
    /// undone, which is why the record is named back to the user first.
    /// </summary>
    private static void DeleteRecord()
    {
        Heading("Delete a record");

        if (register.Count == 0)
        {
            Console.WriteLine("\n  There are no records to delete.");
            Prompt.Pause();
            return;
        }

        int index = SelectRecord("delete");
        Person person = register[index];

        Console.WriteLine();
        if (Prompt.YesNo("Delete " + person + " permanently", false, false))
        {
            register.RemoveAt(index);
            Console.WriteLine("\n  Record deleted.");
        }
        else
        {
            Console.WriteLine("\n  Nothing was deleted.");
        }

        Prompt.Pause();
    }

    // -------------------------------------------------------------------------
    // Sample data
    // -------------------------------------------------------------------------

    /// <summary>
    /// Puts six records into the register, two from each group, so that the
    /// listing, editing and deleting operations have something to work on as
    /// soon as the system starts.
    /// </summary>
    private static void LoadSampleRecords()
    {
        register.Add(new Teacher("Sarah Whitfield", "020 8331 8000",
                                 "s.whitfield@centre.ac.uk", 45200, "Mathematics", "Physics"));
        register.Add(new Teacher("Daniel Osei", "020 8331 8014",
                                 "d.osei@centre.ac.uk", 38750, "English", "History"));

        register.Add(new Admin("Claire Bennett", "020 8331 8022",
                               "c.bennett@centre.ac.uk", 29400, true, 37.5));
        register.Add(new Admin("Marek Nowak", "020 8331 8035",
                               "m.nowak@centre.ac.uk", 15600, false, 20));

        register.Add(new Student("Alice Green", "07700 900123",
                                 "a.green@student.centre.ac.uk",
                                 "Mathematics", "Physics", "Computing"));
        register.Add(new Student("Bilal Rahman", "07700 900456",
                                 "b.rahman@student.centre.ac.uk",
                                 "English", "History", "Economics"));
    }
}
