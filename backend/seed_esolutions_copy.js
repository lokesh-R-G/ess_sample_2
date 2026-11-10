/**
 * ================================================================
 * IDS e SOLUTIONS PRIVATE LIMITED
 * NORMALIZED MASTER DATA SEED
 * ================================================================
 *
 * Database:
 *   essl_production
 *
 * MASTER DATA SEEDED:
 *   1. companies
 *   2. branchs
 *   3. departments
 *   4. designations
 *   5. salary_components
 *   6. employees
 *   7. employee_employment_histories
 *   8. employee_government_ids
 *   9. employee_bank_accounts
 *  10. employee_statutory_profiles
 *  11. employee_salary_components
 *
 * NOT SEEDED:
 *   - payrolls
 *   - payslips
 *   - attendance
 *   - leave transactions
 *   - payroll deductions/results
 *   - PF/ESI remittances
 *   - employee_salary_structures
 *   - employee_ctcs
 *
 * IMPORTANT:
 *   Employee branch/department/designation assignment is stored through
 *   employee_employment_histories.
 *
 *   employee_salary_components uses the business employeeId string
 *   (example: "1001"), NOT employees._id.
 */

require("dotenv").config();

const { MongoClient, ObjectId } = require("mongodb");

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

/*
|--------------------------------------------------------------------------
| COMPANY
|--------------------------------------------------------------------------
*/

const COMPANY = {
    code: "IDS_ESOLUTIONS",
    name: "IDS e SOLUTIONS PRIVATE LIMITED",
    status: "Active",
};

/*
|--------------------------------------------------------------------------
| BRANCH MASTER
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
| DEPARTMENT MASTER
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
| DESIGNATION MASTER
|--------------------------------------------------------------------------
|
| Designation belongs to a department.
|
| IMPORTANT:
| The source data only provides designation names.
| Level values are therefore kept at the default logical level 1.
|
|--------------------------------------------------------------------------
*/

const DESIGNATIONS = [
    {
        name: "M D",
        departmentCode: "FINANCE",
        level: 1,
    },
    {
        name: "General Manager",
        departmentCode: "OPERATION",
        level: 1,
    },
    {
        name: "Sr.System Administrator",
        departmentCode: "NETWORKING",
        level: 1,
    },
    {
        name: "Executive",
        departmentCode: "ACCOUNTS",
        level: 1,
    },
    {
        name: "service Engineer",
        departmentCode: "NETWORKING",
        level: 1,
    },
    {
        name: "Director",
        departmentCode: "MARKETTING",
        level: 1,
    },
    {
        name: "Executive",
        departmentCode: "TENDER",
        level: 1,
    },
];

/*
|--------------------------------------------------------------------------
| EMPLOYEE MASTER
|--------------------------------------------------------------------------
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
| GOVERNMENT IDs
|--------------------------------------------------------------------------
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
| BANK ACCOUNTS
|--------------------------------------------------------------------------
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
| STATUTORY
|--------------------------------------------------------------------------
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
| SALARY MASTER
|--------------------------------------------------------------------------
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
| HELPERS
|--------------------------------------------------------------------------
*/

function parseDate(value) {
    return new Date(`${value}T00:00:00.000Z`);
}

function cleanNumber(value) {
    return Number(value || 0);
}

function safeObjectId(value) {
    if (!value) {
        throw new Error("Missing ObjectId value");
    }

    if (!ObjectId.isValid(value)) {
        throw new Error(`Invalid ObjectId: ${value}`);
    }

    return new ObjectId(value);
}

/*
|--------------------------------------------------------------------------
| MAIN SEED
|--------------------------------------------------------------------------
*/

async function seed() {
    await client.connect();

    const db = client.db(DB_NAME);

    const companies = db.collection("companies");
    const branches = db.collection("branchs");
    const departments = db.collection("departments");
    const designations = db.collection("designations");
    const employees = db.collection("employees");

    const employmentHistories = db.collection(
        "employee_employment_histories"
    );

    const governmentIds = db.collection(
        "employee_government_ids"
    );

    const bankAccounts = db.collection(
        "employee_bank_accounts"
    );

    const statutoryProfiles = db.collection(
        "employee_statutory_profiles"
    );

    const salaryComponents = db.collection(
        "salary_components"
    );

    const employeeSalaryComponents = db.collection(
        "employee_salary_components"
    );

    console.log("\n================================================");
    console.log("IDS e SOLUTIONS NORMALIZED MASTER DATA SEED");
    console.log("================================================\n");

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

    if (!company) {
        throw new Error("Company creation failed");
    }

    const companyId = company._id.toString();

    console.log(
        `✓ Company: ${COMPANY.code} -> ${companyId}`
    );

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
                    status: "Active",
                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
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

        if (!doc) {
            throw new Error(
                `Branch creation failed: ${branch.code}`
            );
        }

        branchMap[branch.code] = doc._id.toString();

        console.log(
            `✓ Branch: ${branch.code} -> ${branch.name}`
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
                    status: "Active",
                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
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

        if (!doc) {
            throw new Error(
                `Department creation failed: ${department.code}`
            );
        }

        departmentMap[department.code] =
            doc._id.toString();

        console.log(
            `✓ Department: ${department.code} -> ${department.name}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 4. DESIGNATIONS
    |--------------------------------------------------------------------------
    |
    | IMPORTANT:
    | "Executive" occurs in multiple departments.
    |
    | Therefore the unique lookup includes departmentId.
    |
    */

    const designationMap = {};

    for (const designation of DESIGNATIONS) {
        const departmentId =
            departmentMap[designation.departmentCode];

        if (!departmentId) {
            throw new Error(
                `Department not found for designation: ${designation.name}`
            );
        }

        await designations.updateOne(
            {
                departmentId,
                name: designation.name,
            },
            {
                $set: {
                    level: designation.level,
                },

                $setOnInsert: {
                    departmentId,
                    name: designation.name,
                },
            },
            { upsert: true }
        );

        const doc = await designations.findOne({
            departmentId,
            name: designation.name,
        });

        if (!doc) {
            throw new Error(
                `Designation creation failed: ${designation.name}`
            );
        }

        const key =
            `${designation.departmentCode}::${designation.name}`;

        designationMap[key] = doc._id.toString();

        console.log(
            `✓ Designation: ${designation.name} -> ${designation.departmentCode}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 5. SALARY COMPONENT MASTER
    |--------------------------------------------------------------------------
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

    for (const definition of componentDefinitions) {
        let component = await salaryComponents.findOne({
            name: definition.name,
        });

        if (!component) {
            await salaryComponents.insertOne({
                name: definition.name,

                componentType: definition.componentType,
                calculationMethod:
                    definition.calculationMethod,

                isTaxable: definition.isTaxable,
                pfApplicable: definition.pfApplicable,
                esiApplicable: definition.esiApplicable,

                attendanceDependent:
                    definition.attendanceDependent,

                isBasicComponent:
                    definition.isBasicComponent,

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
                name: definition.name,
            });
        }

        if (!component) {
            throw new Error(
                `Salary component creation failed: ${definition.name}`
            );
        }

        componentMap[definition.name] =
            component._id.toString();

        console.log(
            `✓ Salary Component: ${definition.name}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 6. HRA -> BASIC RELATIONSHIP
    |--------------------------------------------------------------------------
    */

    const basicComponentId =
        componentMap["BASIC"];

    const hraComponentId =
        componentMap["HRA"];

    await salaryComponents.updateOne(
        {
            _id: safeObjectId(hraComponentId),
        },
        {
            $set: {
                calculationMethod: "Percentage",
                percentageValue: 50,
                percentageDerivedFrom: "BASIC",
                percentageDerivedFromComponentId:
                    basicComponentId,
                updatedAt: NOW,
                updatedBy: SYSTEM_USER,
            },
        }
    );

    console.log("✓ HRA -> BASIC relationship configured");

    /*
    |--------------------------------------------------------------------------
    | 7. EMPLOYEES
    |--------------------------------------------------------------------------
    |
    | IMPORTANT:
    |
    | Branch / Department / Designation assignment is NOT stored as the
    | source of truth here.
    |
    | It is stored in employee_employment_histories.
    |
    */

    for (const employee of EMPLOYEES) {
        const employeeDoc = {
            employeeId: employee.employeeId,
            employeeCode: employee.employeeCode,

            firstName: employee.firstName,
            lastName: employee.lastName,

            email: employee.email,

            /*
             * Personal information supported by the normalized employee model.
             */
            fatherName: employee.fatherName,

            dateOfBirth: parseDate(employee.dob),
            dateOfJoin: parseDate(employee.doj),

            /*
             * These are retained only for legacy/fast-access compatibility
             * because the model supports them.
             *
             * Employment history remains the normalized source.
             */
            branchId: branchMap[employee.branchCode],
            departmentId:
                departmentMap[employee.departmentCode],

            designation: employee.designation,

            systemAccessEnabled:
                employee.systemAccessEnabled,

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
                employeeId: employee.employeeId,
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

        console.log(
            `✓ Employee: ${employee.employeeId} -> ${employee.firstName}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 8. EMPLOYMENT HISTORY
    |--------------------------------------------------------------------------
    |
    | This is the NORMALIZED source for:
    |
    |   Company
    |   Branch
    |   Department
    |   Designation
    |
    */

    for (const employee of EMPLOYEES) {
        const departmentId =
            departmentMap[employee.departmentCode];

        const designationKey =
            `${employee.departmentCode}::${employee.designation}`;

        const designationId =
            designationMap[designationKey];

        const branchId =
            branchMap[employee.branchCode];

        if (!branchId) {
            throw new Error(
                `Branch not found for employee ${employee.employeeId}`
            );
        }

        if (!departmentId) {
            throw new Error(
                `Department not found for employee ${employee.employeeId}`
            );
        }

        if (!designationId) {
            throw new Error(
                `Designation not found for employee ${employee.employeeId}: ${employee.designation}`
            );
        }

        await employmentHistories.updateOne(
            {
                employeeId: employee.employeeId,
                effectiveFrom: parseDate(employee.doj),
            },
            {
                $set: {
                    companyId,
                    branchId,
                    departmentId,
                    designationId,

                    effectiveFrom: parseDate(employee.doj),
                    effectiveTo: null,

                    status: "Active",
                    isCurrent: true,
                    version: 1,

                    dateOfJoining: parseDate(employee.doj),

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                },

                $setOnInsert: {
                    employeeId: employee.employeeId,
                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );

        console.log(
            `✓ Employment History: ${employee.employeeId} -> ${employee.branchCode} / ${employee.departmentCode} / ${employee.designation}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 9. GOVERNMENT IDs
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

                    aadharNumber: null,
                    passportNumber: null,

                    effectiveTo: null,

                    isCurrent: true,
                    status: "Active",
                    version: 1,

                    effectiveFrom: parseDate(employee.doj),

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                },

                $setOnInsert: {
                    employeeId: empNo,

                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );

        console.log(
            `✓ Government IDs: ${empNo}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 10. BANK ACCOUNTS
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

                    bankName: null,
                    branchName: null,
                    ifscCode: null,

                    accountType: "Salary",
                    nameAsPerBank: employee.firstName,

                    effectiveTo: null,

                    isCurrent: true,
                    status: "Active",
                    version: 1,

                    effectiveFrom: parseDate(employee.doj),

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                },

                $setOnInsert: {
                    employeeId: empNo,

                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );

        console.log(
            `✓ Bank Account: ${empNo}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 11. STATUTORY PROFILES
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
                    wantsPf: statutory.wantsPf,
                    wantsPension:
                        statutory.wantsPension,

                    /*
                     * Per audited project compatibility rule.
                     */
                    isExistingPensionMember:
                        statutory.wantsPension,

                    useCeiling:
                        statutory.useCeiling,

                    pfCalculationMode: "Actual",

                    esiEnabled:
                        statutory.esiEnabled,

                    ptState: null,

                    isFresher: false,

                    effectiveFrom:
                        parseDate(employee.doj),

                    effectiveTo: null,

                    isCurrent: true,
                    status: "Active",
                    version: 1,

                    updatedAt: NOW,
                    updatedBy: SYSTEM_USER,
                },

                $setOnInsert: {
                    employeeId: empNo,

                    createdAt: NOW,
                    createdBy: SYSTEM_USER,
                },
            },
            { upsert: true }
        );

        console.log(
            `✓ Statutory Profile: ${empNo}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 12. EMPLOYEE SALARY COMPONENTS
    |--------------------------------------------------------------------------
    |
    | IMPORTANT:
    |
    | employeeId = business employee number.
    |
    | salaryComponentId = salary_components._id converted to string.
    |
    | This collection is the ACTUAL payroll source of truth.
    |
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
                amount: cleanNumber(
                    salary.CONVEYANCES
                ),
            },
            {
                componentName: "MADICAL ALLOWANCE",
                amount: cleanNumber(
                    salary["MADICAL ALLOWANCE"]
                ),
            },
            {
                componentName: "EDU ALLOWANCE",
                amount: cleanNumber(
                    salary["EDU ALLOWANCE"]
                ),
            },
            {
                componentName: "REFE ALLOWANCE",
                amount: cleanNumber(
                    salary["REFE ALLOWANCE"]
                ),
            },
        ];

        const gross = salaryEntries.reduce(
            (sum, item) => sum + item.amount,
            0
        );

        for (const entry of salaryEntries) {
            const componentId =
                componentMap[entry.componentName];

            if (!componentId) {
                throw new Error(
                    `Salary component not found: ${entry.componentName}`
                );
            }

            const componentMaster =
                await salaryComponents.findOne({
                    _id: safeObjectId(componentId),
                });

            if (!componentMaster) {
                throw new Error(
                    `Salary component document missing: ${entry.componentName}`
                );
            }

            const distributionRatio =
                gross > 0
                    ? entry.amount / gross
                    : 0;

            let percentage = null;
            let percentageDerivedFromComponentId =
                null;

            let formulaUsed = "Flat";

            if (entry.componentName === "HRA") {
                percentage = 50;

                percentageDerivedFromComponentId =
                    basicComponentId;

                formulaUsed =
                    "Percentage of BASIC";
            }

            if (entry.componentName === "BASIC") {
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
                        componentCode:
                            componentMaster.code || null,

                        componentName:
                            componentMaster.name,

                        componentType:
                            componentMaster.componentType,

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

                        ptApplicable:
                            componentMaster.ptApplicable ??
                            false,

                        isBasicComponent:
                            componentMaster.isBasicComponent,

                        monthlyAmount:
                            entry.amount,

                        annualAmount:
                            entry.amount * 12,

                        formulaUsed,

                        distributionRatio,

                        effectiveFrom:
                            parseDate(employee.doj),

                        effectiveTo: null,

                        isCurrent: true,

                        status: "Active",

                        version: 1,

                        updatedAt: NOW,
                        updatedBy: SYSTEM_USER,
                    },

                    $setOnInsert: {
                        employeeId: empNo,
                        salaryComponentId: componentId,
                        createdAt: NOW,
                        createdBy: SYSTEM_USER,
                    },
                },
                { upsert: true }
            );
        }

        console.log(
            `✓ Salary: ${empNo} -> Gross Master ₹${gross.toLocaleString(
                "en-IN"
            )}`
        );
    }

    /*
    |--------------------------------------------------------------------------
    | 13. VALIDATION
    |--------------------------------------------------------------------------
    */

    console.log("\n================================================");
    console.log("VALIDATING SEEDED MASTER DATA");
    console.log("================================================\n");

    const companyCount =
        await companies.countDocuments({
            code: COMPANY.code,
        });

    const branchCount =
        await branches.countDocuments({
            companyId,
        });

    const departmentCount =
        await departments.countDocuments({
            companyId,
        });

    const designationCount =
        await designations.countDocuments({});

    const employeeCount =
        await employees.countDocuments({
            employeeId: {
                $in: EMPLOYEES.map(
                    (e) => e.employeeId
                ),
            },
        });

    const employmentHistoryCount =
        await employmentHistories.countDocuments({
            employeeId: {
                $in: EMPLOYEES.map(
                    (e) => e.employeeId
                ),
            },
        });

    const governmentIdCount =
        await governmentIds.countDocuments({
            employeeId: {
                $in: EMPLOYEES.map(
                    (e) => e.employeeId
                ),
            },
            isCurrent: true,
        });

    const bankAccountCount =
        await bankAccounts.countDocuments({
            employeeId: {
                $in: EMPLOYEES.map(
                    (e) => e.employeeId
                ),
            },
            isCurrent: true,
        });

    const statutoryCount =
        await statutoryProfiles.countDocuments({
            employeeId: {
                $in: EMPLOYEES.map(
                    (e) => e.employeeId
                ),
            },
            isCurrent: true,
        });

    const salaryComponentCount =
        await salaryComponents.countDocuments({
            name: {
                $in: componentDefinitions.map(
                    (c) => c.name
                ),
            },
        });

    const employeeSalaryComponentCount =
        await employeeSalaryComponents.countDocuments({
            employeeId: {
                $in: EMPLOYEES.map(
                    (e) => e.employeeId
                ),
            },
            isCurrent: true,
        });

    console.log(
        `Company                  : ${companyCount}`
    );

    console.log(
        `Branches                : ${branchCount} / expected 4`
    );

    console.log(
        `Departments             : ${departmentCount} / expected 6`
    );

    console.log(
        `Designations            : ${designationCount}`
    );

    console.log(
        `Employees               : ${employeeCount} / expected 9`
    );

    console.log(
        `Employment Histories    : ${employmentHistoryCount} / expected 9`
    );

    console.log(
        `Government IDs          : ${governmentIdCount} / expected 9`
    );

    console.log(
        `Bank Accounts           : ${bankAccountCount} / expected 9`
    );

    console.log(
        `Statutory Profiles      : ${statutoryCount} / expected 9`
    );

    console.log(
        `Salary Components       : ${salaryComponentCount} / expected 6`
    );

    console.log(
        `Employee Salary Records : ${employeeSalaryComponentCount} / expected 54`
    );

    /*
    |--------------------------------------------------------------------------
    | 14. TRANSACTIONAL COLLECTION CHECK
    |--------------------------------------------------------------------------
    */

    const payrollCount =
        await db.collection("payrolls").countDocuments({
            // No filter intentionally.
        });

    console.log(
        `\nExisting payroll documents: ${payrollCount}`
    );

    console.log("\n================================================");
    console.log("MASTER DATA SEED COMPLETED");
    console.log("================================================\n");

    console.log("Seeded:");
    console.log("  ✓ companies");
    console.log("  ✓ branchs");
    console.log("  ✓ departments");
    console.log("  ✓ designations");
    console.log("  ✓ salary_components");
    console.log("  ✓ employees");
    console.log(
        "  ✓ employee_employment_histories"
    );
    console.log(
        "  ✓ employee_government_ids"
    );
    console.log(
        "  ✓ employee_bank_accounts"
    );
    console.log(
        "  ✓ employee_statutory_profiles"
    );
    console.log(
        "  ✓ employee_salary_components"
    );

    console.log("\nNOT seeded:");
    console.log("  - payrolls");
    console.log("  - payslips");
    console.log("  - attendance");
    console.log("  - leave transactions");
    console.log("  - payroll deductions/results");
    console.log("  - PF/ESI remittances");
    console.log(
        "  - employee_salary_structures"
    );
    console.log("  - employee_ctcs");
}

/*
|--------------------------------------------------------------------------
| RUN
|--------------------------------------------------------------------------
*/

seed()
    .catch((error) => {
        console.error("\n================================================");
        console.error("SEED FAILED");
        console.error("================================================\n");

        console.error(error);

        process.exitCode = 1;
    })
    .finally(async () => {
        await client.close();
    });