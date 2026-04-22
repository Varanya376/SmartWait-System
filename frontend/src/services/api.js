const BASE_URL = "http://localhost:8000/api";

const options = {
  credentials: "include",
};

//send otp
export async function sendOTP(email) {
  const res = await fetch(`${BASE_URL}/send_otp/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  return await res.json();
}

export async function verifyOTP(email, otp, password) {
  const res = await fetch(`${BASE_URL}/verify_otp/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp, password }),
  });

  return await res.json();
}

//WAIT TIME
export async function fetchWaitTime(restaurantId) {
  const res = await fetch(`${BASE_URL}/predict-wait/${restaurantId}/`, options);

  if (!res.ok) throw new Error("Failed to fetch wait time");

  return await res.json();
}

// RESTAURANTS
export async function fetchRestaurants() {
  const res = await fetch(`${BASE_URL}/restaurants/`, options);

  if (!res.ok) throw new Error("Failed to fetch restaurants");

  return await res.json();
}

//QUEUE
export async function fetchQueue() {
  const res = await fetch(`${BASE_URL}/queue/`, options);

  if (!res.ok) throw new Error("Failed to fetch queue");

  return await res.json();
}

// Notifications

export async function fetchNotifications() {
  const res = await fetch(`${BASE_URL}/notifications/`, {
    credentials: "include",
  });

  if (!res.ok) throw new Error("Failed to fetch notifications");

  return await res.json();
}

export async function subscribeToAlert(restaurantId, threshold = 5) {
  const res = await fetch(`${BASE_URL}/subscribe_alert/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      restaurant: restaurantId,
      threshold: threshold,
    }),
  });

  if (!res.ok) throw new Error("Subscription failed");

  return await res.json();
}

//LOGIN
export async function loginUser(email, password) {
  const res = await fetch(`${BASE_URL}/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error || "Login failed");

  return data;
}

// REGISTER
export async function registerUser(email, password) {
  const res = await fetch(`${BASE_URL}/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error || "Register failed");

  return data;
}

// LOGOUT
export async function logoutUser() {
  const res = await fetch(`${BASE_URL}/logout/`, {
    method: "POST",
    credentials: "include",
  });

  return await res.json();
}

// FORGOT PASSWORD
export async function forgotPassword(email) {
  const res = await fetch(`${BASE_URL}/forgot/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  return await res.json();
}