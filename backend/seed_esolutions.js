/**
 * IDS e SOLUTIONS PRIVATE LIMITED
 * Master Data Seed
 *
 * Database: essl_production
 *
 * Seeds:
 *   - Company
 *   - Branches
 *   - Departments
 *   - Employees
 *   - Government IDs
 *   - Bank Accounts
 *   - Employee Statutory Profiles
 *   - Salary Components
 *   - Employee Salary Components
 *
 * DOES NOT seed:
 *   - July payroll
 *   - Payslips
 *   - Attendance
 *   - Leave transactions
 *   - Payroll deductions/results
 *   - PF/ESI remittance transactions
 */

require("dotenv").config();

const { MongoClient } = require("mongodb");

const MONGODB_URI = "mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0";

if (!MONGODB_URI) {
    throw new Error(
        "Missing MongoDB connection string. Set DATABASE_URL or MONGODB_URI in .env"
    );
}

const DB_NAME = "essl_production";

const client = new MongoClient(MONGODB_URI);

const NOW = new Date();
const SYSTEM_USER = "SYSTEM_SEED";

const COMPANY = {
    code: "IDS_ESOLUTIONS",
    name: "IDS e SOLUTIONS PRIVATE LIMITED",
    status: "Active",
};

/*
|--------------------------------------------------------------------------
| Branch Master
|--------------------------------------------------------------------------
*/

const BRANCHES = [
    {
        code: "BO3301",
        name: "Chennai",
        city: "Chennai",
        state: "Tamil Nadu",
    },
    {
        code: "BO3302",
        name: "Salem",
        city: "Salem",
        state: "Tamil Nadu",
    },
    {
        code: "BO3701",
        name: "Vijayawada",
        city: "Vijayawada",
        state: "Andhra Pradesh",
    },
    {
        code: "BO3303",
        name: "Adyar",
        city: "Chennai",
        state: "Tamil Nadu",
    },
];

/*
|--------------------------------------------------------------------------
| Department Master
|--------------------------------------------------------------------------
*/

const DEPARTMENTS = [
    {
        code: "FINANCE",
        name: "Finance",
    },
    {
        code: "OPERATION",
        name: "Operation",
    },
    {
        code: "NETWORKING",
        name: "Networking",
    },
    {
        code: "ACCOUNTS",
        name: "Accounts",
    },
    {
        code: "MARKETTING",
        name: "Marketting",
    },
    {
        code: "TENDER",
        name: "Tender",
    },
];

/*
|--------------------------------------------------------------------------
| Employee Master
|--------------------------------------------------------------------------
|
| employeeId = Employee No
| employeeCode = Employee No
|
*/

const EMPLOYEES = [
    {
        employeeId: "1001",
        employeeCode: "1001",
        firstName: "C.Saravanakumar",
        lastName: "",
        fatherName: "Shanmugam C A",
        dob: "1973-02-24",
        doj: "2013-09-01",
        branchCode: "BO3301",
        departmentCode: "FINANCE",
        designation: "M D",
        email: "sharan@idschennai.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1021",
        employeeCode: "1021",
        firstName: "Prasanna Prabhu N G",
        lastName: "",
        fatherName: "Gopalakrishna Prabhu A.N",
        dob: "1975-07-14",
        doj: "2013-09-01",
        branchCode: "BO3301",
        departmentCode: "OPERATION",
        designation: "General Manager",
        email: "prasanna4up@rediffmail.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1050",
        employeeCode: "1050",
        firstName: "Badri Narayanan V R",
        lastName: "",
        fatherName: "Ramamurthy V N",
        dob: "1975-05-31",
        doj: "2014-10-01",
        branchCode: "BO3301",
        departmentCode: "NETWORKING",
        designation: "Sr.System Administrator",
        email: "ram91_k@yahoo.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1082",
        employeeCode: "1082",
        firstName: "Latha V",
        lastName: "",
        fatherName: "Vedachalam",
        dob: "1977-12-12",
        doj: "2019-01-11",
        branchCode: "BO3301",
        departmentCode: "ACCOUNTS",
        designation: "Executive",
        email: "vedaslatha@gmail.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1085",
        employeeCode: "1085",
        firstName: "Dhanasekar",
        lastName: "",
        fatherName: "Vadivel",
        dob: "1996-07-28",
        doj: "2023-01-04",
        branchCode: "BO3301",
        departmentCode: "NETWORKING",
        designation: "service Engineer",
        email: "dhana7346@gmail.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1086",
        employeeCode: "1086",
        firstName: "Naveen Raj",
        lastName: "",
        fatherName: "shanmugam A",
        dob: "1999-02-05",
        doj: "2023-01-09",
        branchCode: "BO3301",
        departmentCode: "NETWORKING",
        designation: "service Engineer",
        email: "naveenraj.s.nr82@gmail.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1088",
        employeeCode: "1088",
        firstName: "Arun Kumar.T",
        lastName: "",
        fatherName: "Thirunavukarasau M",
        dob: "1975-03-21",
        doj: "2017-12-01",
        branchCode: "BO3301",
        departmentCode: "MARKETTING",
        designation: "Director",
        email: "arun@idsesolutions.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1089",
        employeeCode: "1089",
        firstName: "Deepika",
        lastName: "",
        fatherName: "Jaganathan",
        dob: "1999-10-22",
        doj: "2026-01-04",
        branchCode: "BO3301",
        departmentCode: "TENDER",
        designation: "Executive",
        email: "7722deepi@gmail.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },

    {
        employeeId: "1090",
        employeeCode: "1090",
        firstName: "Chandana Sampathkumar",
        lastName: "",
        fatherName: "Surendra Sampath Kumar",
        dob: "1982-03-30",
        doj: "2026-04-01",
        branchCode: "BO3701",
        departmentCode: "TENDER",
        designation: "Executive",
        email: "chandanageethika99@gmail.com",
        systemAccessEnabled: false,
        essStatus: "Inactive",
    },
];

/*
|--------------------------------------------------------------------------
| Government IDs
|--------------------------------------------------------------------------
|
| UAN values are taken from the source sheet.
| ESI numbers are NOT present in the source, therefore null.
|
*/

const GOVERNMENT_IDS = {
    "1001": {
        panNumber: "ADEPS4336G",
        uanNumber: null,
        esiNumber: null,
    },

    "1021": {
        panNumber: "ANBPP3720C",
        uanNumber: "101077538260",
        esiNumber: null,
    },

    "1050": {
        panNumber: "AJGPB0041B",
        uanNumber: "101077538304",
        esiNumber: null,
    },

    "1082": {
        panNumber: "ADSPL0913C",
        uanNumber: "101529674372",
        esiNumber: null,
    },

    "1085": {
        panNumber: "EYKPD7013L",
        uanNumber: "101842730454",
        esiNumber: null,
    },

    "1086": {
        panNumber: "BUWPN9987L",
        uanNumber: "101309114913",
        esiNumber: null,
    },

    "1088": {
        panNumber: "ADPPA3101Q",
        uanNumber: "101232723469",
        esiNumber: null,
    },

    "1089": {
        panNumber: "GJNPD6623Q",
        uanNumber: "102319596308",
        esiNumber: null,
    },

    "1090": {
        panNumber: "DXMPS3548P",
        uanNumber: "102320153772",
        esiNumber: null,
    },
};

/*
|--------------------------------------------------------------------------
| Bank Accounts
|--------------------------------------------------------------------------
|
| Only account number is available from the source.
| Bank name / IFSC / branch are therefore null.
|
*/

const BANK_ACCOUNTS = {
    "1001": {
        accountNumber: "2524000100127826",
    },

    "1021": {
        accountNumber: "1207010300041977",
    },

    "1050": {
        accountNumber: "2524000103044793",
    },

    "1082": {
        accountNumber: "2524000103085976",
    },

    "1085": {
        accountNumber: "2524000103093036",
    },

    "1086": {
        accountNumber: "2524000103094512",
    },

    "1088": {
        accountNumber: "2524000102987792",
    },

    "1089": {
        accountNumber: "2524000400013106",
    },

    "1090": {
        accountNumber: "0465006900003171",
    },
};

/*
|--------------------------------------------------------------------------
| Statutory Configuration
|--------------------------------------------------------------------------
|
| PF ceiling:
|   Excel Yes -> useCeiling true
|   Excel No  -> useCeiling false
|
| PT state:
|   Confirmed by user -> null
|
*/

const STATUTORY = {
    "1001": {
        wantsPf: false,
        wantsPension: false,
        useCeiling: false,
        esiEnabled: false,
    },

    "1021": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },

    "1050": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },

    "1082": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },

    "1085": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },

    "1086": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },

    "1088": {
        wantsPf: false,
        wantsPension: false,
        useCeiling: false,
        esiEnabled: false,
    },

    "1089": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },

    "1090": {
        wantsPf: true,
        wantsPension: true,
        useCeiling: true,
        esiEnabled: true,
    },
};

/*
|--------------------------------------------------------------------------
| Salary Master
|--------------------------------------------------------------------------
|
| These are the MASTER salary amounts from the employee section.
|
| Not the July payroll result.
|
*/

const SALARY = {
    "1001": {
        BASIC: 34000,
        HRA: 17000,
        CONVEYANCES: 6000,
        "MADICAL ALLOWANCE": 6000,
        "EDU ALLOWANCE": 6000,
        "REFE ALLOWANCE": 6000,
    },

    "1021": {
        BASIC: 52500,
        HRA: 26250,
        CONVEYANCES: 8000,
        "MADICAL ALLOWANCE": 7000,
        "EDU ALLOWANCE": 7000,
        "REFE ALLOWANCE": 2693,
    },

    "1050": {
        BASIC: 16000,
        HRA: 8000,
        CONVEYANCES: 7000,
        "MADICAL ALLOWANCE": 7000,
        "EDU ALLOWANCE": 7000,
        "REFE ALLOWANCE": 5000,
    },

    "1082": {
        BASIC: 8704,
        HRA: 4352,
        CONVEYANCES: 1000,
        "MADICAL ALLOWANCE": 1027,
        "EDU ALLOWANCE": 0,
        "REFE ALLOWANCE": 0,
    },

    "1085": {
        BASIC: 15158,
        HRA: 7579,
        CONVEYANCES: 1500,
        "MADICAL ALLOWANCE": 1500,
        "EDU ALLOWANCE": 0,
        "REFE ALLOWANCE": 525,
    },

    "1086": {
        BASIC: 10823,
        HRA: 5412,
        CONVEYANCES: 1000,
        "MADICAL ALLOWANCE": 500,
        "EDU ALLOWANCE": 0,
        "REFE ALLOWANCE": 561,
    },

    "1088": {
        BASIC: 52500,
        HRA: 26250,
        CONVEYANCES: 8000,
        "MADICAL ALLOWANCE": 8000,
        "EDU ALLOWANCE": 7000,
        "REFE ALLOWANCE": 1693,
    },

    "1089": {
        BASIC: 6028,
        HRA: 3014,
        CONVEYANCES: 1100,
        "MADICAL ALLOWANCE": 0,
        "EDU ALLOWANCE": 0,
        "REFE ALLOWANCE": 0,
    },

    "1090": {
        BASIC: 6000,
        HRA: 3000,
        CONVEYANCES: 0,
        "MADICAL ALLOWANCE": 0,
        "EDU ALLOWANCE": 0,
        "REFE ALLOWANCE": 0,
    },
};

/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function parseDate(value) {
    return new Date(`${value}T00:00:00.000Z`);
}

function cleanNumber(value) {
    return Number(value || 0);
}

/*
|--------------------------------------------------------------------------
| Main Seed
|--------------------------------------------------------------------------
*/

async function seed() {
    await client.connect();

    const db = client.db(DB_NAME);

    const companies = db.collection("companies");
    const branches = db.collection("branchs");
    const departments = db.collection("departments");
    const employees = db.collection("employees");
    const governmentIds = db.collection("employee_government_ids");
    const bankAccounts = db.collection("employee_bank_accounts");
    const statutoryProfiles = db.collection("employee_statutory_profiles");
    const salaryComponents = db.collection("salary_components");
    const employeeSalaryComponents =
        db.collection("employee_salary_components");

    console.log("\n========================================");
    console.log("IDS e SOLUTIONS MASTER DATA SEED");
    console.log("========================================\n");

    /*
    |--------------------------------------------------------------------------
    | 1. COMPANY
    |--------------------------------------------------------------------------
    */

    await companies.updateOne(
        { code: COMPANY.code },
        {
            $set: {
                name: COMPANY.name,
                status: COMPANY.status,
                updatedAt: NOW,
                updatedBy: SYSTEM_USER,
            },
            $setOnInsert: {
                code: COMPANY.code,
                createdAt: NOW,
                createdBy: SYSTEM_USER,
            },
        },
        { upsert: true }
    );

    const company = await companies.findOne({
        code: COMPANY.code,
    });

    const companyId = company._id.toString();

    console.log(`Company: ${COMPANY.name}`);
    console.log(`Company ID: ${companyId}`);

    /*
    |--------------------------------------------------------------------------
    | 2. BRANCHES
    |--------------------------------------------------------------------------
    */

    const branchMap = {};

    for (const branch of BRANCHES) {
        await branches.updateOne(
            {
                companyId,
                code: branch.code,
            },
            {
                $set: {
                    name: branch.name,
                    city: branch.city,
                    state: branch.state,
                    country: "India",
                    attendanceEnabled: false,
                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                    status: "Active",
                },
                $setOnInsert: {
                    companyId,
                    code: branch.code,
                    address: null,
                    pincode: null,
                    esslMachineId: null,
                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );

        const doc = await branches.findOne({
            companyId,
            code: branch.code,
        });

        branchMap[branch.code] = doc._id.toString();

        console.log(
            `Branch: ${branch.code} -> ${branch.name} (${branchMap[branch.code]})`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 3. DEPARTMENTS
    |--------------------------------------------------------------------------
    */

    const departmentMap = {};

    for (const department of DEPARTMENTS) {
        await departments.updateOne(
            {
                companyId,
                code: department.code,
            },
            {
                $set: {
                    name: department.name,
                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                    status: "Active",
                },
                $setOnInsert: {
                    companyId,
                    code: department.code,
                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );

        const doc = await departments.findOne({
            companyId,
            code: department.code,
        });

        departmentMap[department.code] = doc._id.toString();

        console.log(
            `Department: ${department.code} -> ${department.name}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 4. SALARY COMPONENT MASTER
    |--------------------------------------------------------------------------
    |
    | Reuse existing components whenever possible.
    |
    */

    const componentMap = {};

    const componentDefinitions = [
        {
            name: "BASIC",
            componentType: "Earning",
            calculationMethod: "Flat",
            isBasicComponent: true,
            isTaxable: true,
            pfApplicable: true,
            esiApplicable: true,
            attendanceDependent: true,
            displayOrder: 1,
        },

        {
            name: "HRA",
            componentType: "Earning",
            calculationMethod: "Percentage",
            percentageValue: 50,
            percentageDerivedFrom: "BASIC",
            isBasicComponent: false,
            isTaxable: true,
            pfApplicable: false,
            esiApplicable: true,
            attendanceDependent: true,
            displayOrder: 2,
        },

        {
            name: "CONVEYANCES",
            componentType: "Earning",
            calculationMethod: "Flat",
            isBasicComponent: false,
            isTaxable: true,
            pfApplicable: true,
            esiApplicable: true,
            attendanceDependent: true,
            displayOrder: 3,
        },

        {
            name: "MADICAL ALLOWANCE",
            componentType: "Earning",
            calculationMethod: "Flat",
            isBasicComponent: false,
            isTaxable: true,
            pfApplicable: true,
            esiApplicable: true,
            attendanceDependent: false,
            displayOrder: 4,
        },

        {
            name: "EDU ALLOWANCE",
            componentType: "Earning",
            calculationMethod: "Flat",
            isBasicComponent: false,
            isTaxable: true,
            pfApplicable: true,
            esiApplicable: true,
            attendanceDependent: false,
            displayOrder: 5,
        },

        {
            name: "REFE ALLOWANCE",
            componentType: "Earning",
            calculationMethod: "Flat",
            isBasicComponent: false,
            isTaxable: true,
            pfApplicable: true,
            esiApplicable: true,
            attendanceDependent: true,
            displayOrder: 6,
        },
    ];

    /*
     * Find existing component names case-insensitively,
     * otherwise create them.
     */
    for (const definition of componentDefinitions) {
        let component = await salaryComponents.findOne({
            name: {
                $regex: `^${definition.name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`,
                $options: "i",
            },
        });

        if (!component) {
            const insertResult = await salaryComponents.insertOne({
                name: definition.name,
                componentType: definition.componentType,
                calculationMethod: definition.calculationMethod,

                isTaxable: definition.isTaxable,
                pfApplicable: definition.pfApplicable,
                esiApplicable: definition.esiApplicable,

                attendanceDependent: definition.attendanceDependent,
                isBasicComponent: definition.isBasicComponent,

                code: null,
                defaultFormula: null,

                percentageDerivedFrom:
                    definition.percentageDerivedFrom || null,

                percentageDerivedFromComponentId: null,

                percentageValue:
                    definition.percentageValue ?? null,

                displayOrder: definition.displayOrder,

                isActive: true,
                status: "Active",

                createdAt: NOW,
                updatedAt: NOW,
                createdBy: SYSTEM_USER,
                updatedBy: SYSTEM_USER,
            });

            component = await salaryComponents.findOne({
                _id: insertResult.insertedId,
            });
        }

        componentMap[definition.name] = component._id.toString();

        console.log(
            `Salary Component: ${definition.name} -> ${componentMap[definition.name]}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | Link HRA -> BASIC
    |--------------------------------------------------------------------------
    */

    const basicComponentId = componentMap["BASIC"];

    await salaryComponents.updateOne(
        {
            _id: basicComponentId
                ? new (require("mongodb").ObjectId)(basicComponentId)
                : null,
        },
        {
            $set: {
                updatedAt: NOW,
                updatedBy: SYSTEM_USER,
            },
        }
    );

    await salaryComponents.updateOne(
        {
            _id: new (require("mongodb").ObjectId)(
                componentMap["HRA"]
            ),
        },
        {
            $set: {
                calculationMethod: "Percentage",
                percentageValue: 50,
                percentageDerivedFrom: "BASIC",
                percentageDerivedFromComponentId: basicComponentId,
                updatedAt: NOW,
                updatedBy: SYSTEM_USER,
            },
        }
    );

    /*
    |--------------------------------------------------------------------------
    | 5. EMPLOYEES
    |--------------------------------------------------------------------------
    */

    const employeeMap = {};

    for (const employee of EMPLOYEES) {
        const employeeDoc = {
            employeeId: employee.employeeId,
            employeeCode: employee.employeeCode,

            firstName: employee.firstName,
            lastName: employee.lastName,

            email: employee.email,

            branchId: branchMap[employee.branchCode],
            departmentId: departmentMap[employee.departmentCode],

            designation: employee.designation,
            fatherName: employee.fatherName,

            dateOfBirth: parseDate(employee.dob),
            dateOfJoin: parseDate(employee.doj),

            systemAccessEnabled: employee.systemAccessEnabled,
            essStatus: employee.essStatus,

            isActive: true,
            isCurrent: true,

            effectiveFrom: parseDate(employee.doj),
            effectiveTo: null,

            status: "Active",
            version: 1,

            updatedAt: NOW,
            updatedBy: SYSTEM_USER,
        };

        await employees.updateOne(
            {
                employeeCode: employee.employeeCode,
            },
            {
                $set: employeeDoc,

                $setOnInsert: {
                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                    authUserId: null,
                },
            },
            { upsert: true }
        );

        const savedEmployee = await employees.findOne({
            employeeCode: employee.employeeCode,
        });

        employeeMap[employee.employeeId] = savedEmployee._id.toString();

        console.log(
            `Employee: ${employee.employeeCode} -> ${employee.firstName}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 6. GOVERNMENT IDs
    |--------------------------------------------------------------------------
    */

    for (const employee of EMPLOYEES) {
        const empNo = employee.employeeId;
        const government = GOVERNMENT_IDS[empNo];

        await governmentIds.updateOne(
            {
                employeeId: empNo,
                isCurrent: true,
            },
            {
                $set: {
                    panNumber: government.panNumber,
                    uanNumber: government.uanNumber,
                    esiNumber: government.esiNumber,

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,

                    status: "Active",
                    version: 1,
                    isCurrent: true,

                    effectiveTo: null,
                },

                $setOnInsert: {
                    employeeId: empNo,
                    aadharNumber: null,
                    passportNumber: null,

                    createdAt: NOW,
                    createdBy: SYSTEM_USER,

                    effectiveFrom: parseDate(employee.doj),
                },
            },
            { upsert: true }
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 7. BANK ACCOUNTS
    |--------------------------------------------------------------------------
    */

    for (const employee of EMPLOYEES) {
        const empNo = employee.employeeId;
        const bank = BANK_ACCOUNTS[empNo];

        await bankAccounts.updateOne(
            {
                employeeId: empNo,
                isCurrent: true,
            },
            {
                $set: {
                    accountNumber: bank.accountNumber,

                    /*
                     * These values are intentionally null because
                     * the source sheet does not contain them.
                     */
                    bankName: null,
                    branchName: null,
                    ifscCode: null,

                    accountType: "Salary",
                    nameAsPerBank: employee.firstName,

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,

                    status: "Active",
                    version: 1,
                    isCurrent: true,

                    effectiveTo: null,
                },

                $setOnInsert: {
                    employeeId: empNo,
                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                    effectiveFrom: parseDate(employee.doj),
                },
            },
            { upsert: true }
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 8. EMPLOYEE STATUTORY PROFILES
    |--------------------------------------------------------------------------
    */

    for (const employee of EMPLOYEES) {
        const empNo = employee.employeeId;
        const statutory = STATUTORY[empNo];

        await statutoryProfiles.updateOne(
            {
                employeeId: empNo,
                isCurrent: true,
            },
            {
                $set: {
                    effectiveTo: null,

                    status: "Active",
                    version: 1,
                    isCurrent: true,

                    isFresher: false,

                    isExistingPensionMember:
                        statutory.wantsPension,

                    wantsPf: statutory.wantsPf,
                    wantsPension: statutory.wantsPension,

                    pfCalculationMode: statutory.wantsPf
                        ? "Actual"
                        : "Actual",

                    useCeiling: statutory.useCeiling,

                    esiEnabled: statutory.esiEnabled,

                    /*
                     * User explicitly requested PT state = null.
                     */
                    ptState: null,

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                },

                $setOnInsert: {
                    employeeId: empNo,

                    effectiveFrom: parseDate(employee.doj),

                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 9. EMPLOYEE SALARY COMPONENTS
    |--------------------------------------------------------------------------
    */

    for (const employee of EMPLOYEES) {
        const empNo = employee.employeeId;
        const salary = SALARY[empNo];

        const salaryEntries = [
            {
                componentName: "BASIC",
                amount: cleanNumber(salary.BASIC),
            },
            {
                componentName: "HRA",
                amount: cleanNumber(salary.HRA),
            },
            {
                componentName: "CONVEYANCES",
                amount: cleanNumber(salary.CONVEYANCES),
            },
            {
                componentName: "MADICAL ALLOWANCE",
                amount: cleanNumber(salary["MADICAL ALLOWANCE"]),
            },
            {
                componentName: "EDU ALLOWANCE",
                amount: cleanNumber(salary["EDU ALLOWANCE"]),
            },
            {
                componentName: "REFE ALLOWANCE",
                amount: cleanNumber(salary["REFE ALLOWANCE"]),
            },
        ];

        const gross = salaryEntries.reduce(
            (sum, item) => sum + item.amount,
            0
        );

        for (const entry of salaryEntries) {
            const componentId = componentMap[entry.componentName];

            if (!componentId) {
                throw new Error(
                    `Salary component not found: ${entry.componentName}`
                );
            }

            const componentObjectId = new (require("mongodb").ObjectId)(
                componentId
            );

            const componentMaster = await salaryComponents.findOne({
                _id: componentObjectId,
            });

            if (!componentMaster) {
                throw new Error(
                    `Salary component document missing: ${entry.componentName}`
                );
            }

            const distributionRatio =
                gross > 0 ? entry.amount / gross : 0;

            let percentage = null;
            let percentageDerivedFromComponentId = null;
            let formulaUsed = "Flat";

            if (entry.componentName === "HRA") {
                percentage = 50;
                percentageDerivedFromComponentId = basicComponentId;
                formulaUsed = "Percentage of BASIC";
            } else if (entry.componentName === "BASIC") {
                formulaUsed = "Base Input";
            }

            await employeeSalaryComponents.updateOne(
                {
                    employeeId: empNo,
                    salaryComponentId: componentId,
                    isCurrent: true,
                },
                {
                    $set: {
                        componentCode: componentMaster.code || null,

                        componentName: componentMaster.name,
                        componentType: componentMaster.componentType,
                        calculationMethod:
                            componentMaster.calculationMethod,

                        percentage,
                        percentageDerivedFromComponentId,

                        includeInGross: true,

                        attendanceDependent:
                            componentMaster.attendanceDependent,

                        pfApplicable:
                            componentMaster.pfApplicable,

                        esiApplicable:
                            componentMaster.esiApplicable,

                        ptApplicable: false,

                        isBasicComponent:
                            componentMaster.isBasicComponent,

                        monthlyAmount: entry.amount,
                        annualAmount: entry.amount * 12,

                        formulaUsed,

                        distributionRatio,

                        effectiveFrom: parseDate(employee.doj),
                        effectiveTo: null,

                        isCurrent: true,
                        status: "Active",
                        version: 1,
                    },

                    $setOnInsert: {
                        employeeId: empNo,
                        salaryComponentId: componentId,
                    },
                },
                { upsert: true }
            );
        }

        console.log(
            `Salary: ${empNo} -> Gross Master ₹${gross.toLocaleString("en-IN")}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 10. SUMMARY
    |--------------------------------------------------------------------------
    */

    console.log("\n========================================");
    console.log("SEED COMPLETED");
    console.log("========================================");

    console.log(`Company       : ${COMPANY.name}`);
    console.log(`Company Code  : ${COMPANY.code}`);
    console.log(`Branches      : ${BRANCHES.length}`);
    console.log(`Departments   : ${DEPARTMENTS.length}`);
    console.log(`Employees     : ${EMPLOYEES.length}`);
    console.log(`Database      : ${DB_NAME}`);

    console.log("\nSeeded collections:");
    console.log("  companies");
    console.log("  branchs");
    console.log("  departments");
    console.log("  employees");
    console.log("  employee_government_ids");
    console.log("  employee_bank_accounts");
    console.log("  employee_statutory_profiles");
    console.log("  salary_components");
    console.log("  employee_salary_components");

    console.log("\nNOT seeded:");
    console.log("  payrolls");
    console.log("  payslips");
    console.log("  attendance");
    console.log("  leave transactions");
    console.log("  PF/ESI remittances");

    console.log("\n");
}

/*
|--------------------------------------------------------------------------
| Run
|--------------------------------------------------------------------------
*/

seed()
    .catch((error) => {
        console.error("\nSEED FAILED\n");
        console.error(error);
        process.exitCode = 1;
    })
    .finally(async () => {
        await client.close();
    });