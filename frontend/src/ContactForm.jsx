import { useState } from "react";

const ContactForm = ({ existingContact = {}, updateCallback }) => {
    const [firstName, setFirstName] = useState(existingContact.firstName || "");
    const [lastName, setLastName] = useState(existingContact.lastName || "");
    const [email, setEmail] = useState(existingContact.email || "");

    const updating = Object.entries(existingContact).length !== 0;

    const onSubmit = async (e) => {
        e.preventDefault();

        const data = {
            firstName,
            lastName,
            email,
        };
        const url = `http://127.0.0.1:5000/${
            updating ? `update_contact/${existingContact.id}` : "create_contact"
        }`;
        const options = {
            method: updating ? "PATCH" : "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
            credentials: "include", // Include cookies for session
        };
        const response = await fetch(url, options);
        if (response.status !== 201 && response.status !== 200) {
            const data = await response.json();
            alert(data.message);
        } else {
            updateCallback();
        }
    };

    return (
        <form onSubmit={onSubmit} className="space-y-4">
            <div>
                <label htmlFor="firstName" className="block text-sm font-medium">
                    First Name:
                </label>
                <input
                    type="text"
                    id="firstName"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="mt-1 p-2 border rounded w-full"
                />
            </div>
            <div>
                <label htmlFor="lastName" className="block text-sm font-medium">
                    Last Name:
                </label>
                <input
                    type="text"
                    id="lastName"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="mt-1 p-2 border rounded w-full"
                />
            </div>
            <div>
                <label htmlFor="email" className="block text-sm font-medium">
                    Email:
                </label>
                <input
                    type="text"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="mt-1 p-2 border rounded w-full"
                />
            </div>
            <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
                {updating ? "Update" : "Create"}
            </button>
        </form>
    );
};

export default ContactForm;