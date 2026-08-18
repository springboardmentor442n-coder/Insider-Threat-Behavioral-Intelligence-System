const API_URL = "http://127.0.0.1:8000";

export async function predictUser(data) {
    const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error("Prediction failed");
    }

    return await response.json();
}

export async function getEmployeeAnalysis(employeeId) {
    const response = await fetch(`${API_URL}/employees/${employeeId}/analysis`, {
        method: "GET",
    });

    if (!response.ok) {
        throw new Error("Failed to fetch employee analysis");
    }

    return await response.json();
}

export async function predictBatch(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/batch-predict`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Batch prediction failed");
    }

    return await response.json();
}