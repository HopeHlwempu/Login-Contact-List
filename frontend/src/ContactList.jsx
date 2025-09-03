import React from "react";

const ContactList = ({ contacts, updateContact, updateCallback }) => {
    const onDelete = async (id) => {
        try {
            const token = localStorage.getItem("token");
            const options = {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            };
            const response = await fetch(
                `http://127.0.0.1:5000/delete_contact/${id}`,
                options
            );
            if (response.status === 200) {
                updateCallback();
            } else {
                console.error("Failed to delete");
            }
        } catch (error) {
            alert(error);
        }
    };

    return (
        <div className="mb-4">
            <h2 className="text-xl font-bold mb-2">Contacts</h2>
            <table className="table-auto w-full border-collapse border">
                <thead>
                    <tr className="bg-gray-200">
                        <th className="border p-2">First Name</th>
                        <th className="border p-2">Last Name</th>
                        <th className="border p-2">Email</th>
                        <th className="border p-2">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {contacts.map((contact) => (
                        <tr key={contact.id}>
                            <td className="border p-2">{contact.firstName}</td>
                            <td className="border p-2">{contact.lastName}</td>
                            <td className="border p-2">{contact.email}</td>
                            <td className="border p-2">
                                <button
                                    className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-1 px-2 rounded mr-2"
                                    onClick={() => updateContact(contact)}
                                >
                                    Update
                                </button>
                                <button
                                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded"
                                    onClick={() => onDelete(contact.id)}
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ContactList;