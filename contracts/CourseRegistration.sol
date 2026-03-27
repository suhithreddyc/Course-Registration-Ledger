// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CourseRegistration {

    address public admin;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this");
        _;
    }

    struct Course {
        string  courseId;
        string  courseName;
        uint256 totalSeats;
        uint256 enrolledCount;
        bool    isActive;
    }

    struct Student {
        string  studentId;
        address wallet;
        bool    isRegistered;
    }

    struct TxRecord {
        uint256 timestamp;
        string  studentId;
        string  courseId;
        string  action;
        bool    success;
    }

    mapping(string => Course)   public courses;
    mapping(address => Student) public students;
    mapping(string => bool)     public studentIdExists;
    mapping(string => address)  public studentIdToWallet;
    mapping(string => mapping(string => bool)) public enrollments;
    mapping(string => uint256) public studentCourseCount;

    string[]    public courseList;
    TxRecord[]  public ledger;

    uint256 public constant MAX_COURSES_PER_STUDENT = 4;
    uint256 public registrationStart;
    uint256 public registrationEnd;

    event StudentRegistered(string studentId, address wallet);
    event CourseAdded(string courseId, string courseName, uint256 seats);
    event Enrolled(string studentId, string courseId, uint256 remainingSeats);
    event Dropped(string studentId, string courseId, uint256 remainingSeats);
    event SeatUpdated(string courseId, uint256 newTotal);

    constructor() {
        admin = msg.sender;
        _addCourse("CC",    "Cloud Computing",                    40);
        _addCourse("OOAD",  "Object Oriented Analysis & Design",  35);
        _addCourse("CD",    "Compiler Design",                    30);
        _addCourse("MAR",   "Marketing Analytics",                25);
        _addCourse("BC",    "Blockchain & Cryptography",          20);
        _addCourse("GenAI", "Generative AI",                      15);
        _addCourse("DBT",   "Database Technologies",              30);
        _addCourse("DT",    "Digital Transformation",             20);
        _addCourse("DF",    "Digital Forensics",                  20);
        registrationStart = 0;
        registrationEnd   = 0;
    }

    function _addCourse(string memory id, string memory name, uint256 seats) internal {
        courses[id] = Course(id, name, seats, 0, true);
        courseList.push(id);
        emit CourseAdded(id, name, seats);
    }

    function setRegistrationWindow(uint256 start, uint256 end) external onlyAdmin {
        require(end == 0 || end > start, "Invalid window");
        registrationStart = start;
        registrationEnd   = end;
    }

    function addCourse(string memory courseId, string memory courseName, uint256 totalSeats)
        external onlyAdmin
    {
        require(bytes(courses[courseId].courseId).length == 0, "Course already exists");
        require(totalSeats > 0, "Seats must be > 0");
        _addCourse(courseId, courseName, totalSeats);
    }

    function updateSeats(string memory courseId, uint256 newTotal) external onlyAdmin {
        require(bytes(courses[courseId].courseId).length != 0, "Course not found");
        require(newTotal >= courses[courseId].enrolledCount, "Cannot reduce below enrolled");
        courses[courseId].totalSeats = newTotal;
        emit SeatUpdated(courseId, newTotal);
    }

    function toggleCourse(string memory courseId, bool active) external onlyAdmin {
        require(bytes(courses[courseId].courseId).length != 0, "Course not found");
        courses[courseId].isActive = active;
    }

    function registerStudent(string memory studentId) external {
        require(!students[msg.sender].isRegistered, "Wallet already registered");
        require(!studentIdExists[studentId],         "Student ID already taken");
        require(bytes(studentId).length > 0,         "Student ID cannot be empty");
        students[msg.sender]         = Student(studentId, msg.sender, true);
        studentIdExists[studentId]   = true;
        studentIdToWallet[studentId] = msg.sender;
        emit StudentRegistered(studentId, msg.sender);
    }

    function enroll(string memory courseId) external {
        if (registrationStart != 0 || registrationEnd != 0) {
            require(block.timestamp >= registrationStart, "Registration not open yet");
            require(registrationEnd == 0 || block.timestamp <= registrationEnd, "Registration closed");
        }
        Student storage stu = students[msg.sender];
        require(stu.isRegistered,                         "Student not registered");
        Course storage crs = courses[courseId];
        require(bytes(crs.courseId).length != 0,          "Course not found");
        require(crs.isActive,                             "Course is not active");
        require(crs.enrolledCount < crs.totalSeats,       "No seats available");
        require(!enrollments[stu.studentId][courseId],    "Already enrolled");
        require(studentCourseCount[stu.studentId] < MAX_COURSES_PER_STUDENT, "Max 4 courses reached");

        crs.enrolledCount++;
        enrollments[stu.studentId][courseId] = true;
        studentCourseCount[stu.studentId]++;
        ledger.push(TxRecord(block.timestamp, stu.studentId, courseId, "ENROLL", true));
        emit Enrolled(stu.studentId, courseId, crs.totalSeats - crs.enrolledCount);
    }

    function drop(string memory courseId) external {
        Student storage stu = students[msg.sender];
        require(stu.isRegistered,                      "Student not registered");
        require(enrollments[stu.studentId][courseId],  "Not enrolled in this course");
        Course storage crs = courses[courseId];
        crs.enrolledCount--;
        enrollments[stu.studentId][courseId] = false;
        studentCourseCount[stu.studentId]--;
        ledger.push(TxRecord(block.timestamp, stu.studentId, courseId, "DROP", true));
        emit Dropped(stu.studentId, courseId, crs.totalSeats - crs.enrolledCount);
    }

    function getCourseIds() external view returns (string[] memory) { return courseList; }

    function getCourse(string memory courseId)
        external view returns (string memory, string memory, uint256, uint256, uint256, bool)
    {
        Course storage c = courses[courseId];
        require(bytes(c.courseId).length != 0, "Course not found");
        return (c.courseId, c.courseName, c.totalSeats, c.enrolledCount,
                c.totalSeats - c.enrolledCount, c.isActive);
    }

    function isEnrolled(string memory studentId, string memory courseId)
        external view returns (bool)
    { return enrollments[studentId][courseId]; }

    function getLedgerLength() external view returns (uint256) { return ledger.length; }

    function getLedgerEntry(uint256 index)
        external view returns (uint256, string memory, string memory, string memory, bool)
    {
        require(index < ledger.length, "Out of range");
        TxRecord storage t = ledger[index];
        return (t.timestamp, t.studentId, t.courseId, t.action, t.success);
    }

    function getStudentInfo(address wallet)
        external view returns (string memory, bool, uint256)
    {
        Student storage s = students[wallet];
        return (s.studentId, s.isRegistered, studentCourseCount[s.studentId]);
    }

    function getRegistrationWindow()
        external view returns (uint256, uint256, bool)
    {
        bool open = (registrationStart == 0 && registrationEnd == 0)
                 || (block.timestamp >= registrationStart
                     && (registrationEnd == 0 || block.timestamp <= registrationEnd));
        return (registrationStart, registrationEnd, open);
    }
}