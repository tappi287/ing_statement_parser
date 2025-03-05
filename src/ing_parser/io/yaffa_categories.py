from dataclasses import dataclass, field

@dataclass
class System1:
    income_categories: list[str] = field(default_factory=lambda: ["Salary", "Other Income"])
    expense_categories: list[str] = field(default_factory=lambda: [
        "Housing",
        "Utilities",
        "Groceries",
        "Transportation",
        "Entertainment",
        "Healthcare",
        "Insurance",
        "Clothing"
    ])

@dataclass
class System2:
    income_categories: dict[str, list[str]] = field(default_factory=lambda: {
        "Salary": ["Main Job", "Bonuses"],
        "Other Income": ["Side Job", "Rental income"]
    })
    expense_categories: dict[str, list[str]] = field(default_factory=lambda: {
        "Housing": ["Rent/Mortgage", "Maintenance/Repairs"],
        "Utilities": ["Electricity", "Water", "Gas/Heating"],
        "Groceries": ["Food", "Household Supplies"],
        "Transportation": ["Public Transport", "Fuel", "Vehicle Maintenance"],
        "Entertainment": ["Dining Out", "Subscriptions (streaming, music)", "Events (movies, concerts)"],
        "Healthcare": ["Doctor Visits", "Medications", "Health Insurance"],
        "Insurance": ["Home Insurance", "Car Insurance"],
        "Debt Repayment": ["Credit Cards", "Loans"]
    })

@dataclass
class System3:
    income_categories: dict[str, list[str]] = field(default_factory=lambda: {
        "Salary": ["Main Job", "Bonuses"],
        "Other Income": [
            "Freelance Work",
            "Rental Income",
            "Government Benefits",
            "Child Allowance",
            "Social Assistance"
        ]
    })
    expense_categories: dict[str, list[str]] = field(default_factory=lambda: {
        "Housing": ["Rent", "Property Taxes", "Repairs/Maintenance", "Home Improvements"],
        "Utilities": [
            "Electricity",
            "Gas/Heating",
            "Water/Sewer",
            "Internet/Cable"
        ],
        "Groceries": ["Food", "Household Products", "Personal Care"],
        "Clothing": [],
        "Transportation": [
            "Car Payments",
            "Public Transport",
            "Fuel",
            "Parking",
            "Maintenance/Repairs"
        ],
        "Entertainment & Leisure": [
            "Dining Out",
            "Subscriptions (TV, music, gym)",
            "Hobbies/Activities",
            "Vacations/Travel",
            "Events (concerts, cinema, theater)"
        ],
        "Healthcare": ["Doctor/Dentist Visits", "Medications", "Health Insurance Premiums", "Vision/Dental Care"],
        "Insurance": [
            "Home Insurance",
            "Auto Insurance",
            "Life Insurance",
            "Disability Insurance"
        ],
        "Debt Repayment": ["Credit Card", "Student Loans", "Personal Loans", "Mortgage Overpayments"],
        "Education & Development": ["Courses/Training", "Books/Supplies", "School/University Fees"],
        "Miscellaneous": [
            "Gifts/Donations",
            "Pet Care",
            "Fines",
            "Legal Fees"
        ]
    })