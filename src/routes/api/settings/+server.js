// import { json } from "@sveltejs/kit";
// import { settings } from "$lib/server/db.js"; // Import from server-side db


// // Helper functions for database operations
// export const addSleepSetting = (sleepTime, wakeTime, date) => {
//   const stmt = settings.prepare(
//     'INSERT INTO sleep_records (sleep_time, wake_time, date) VALUES (?, ?, ?)'
//   );
//   return stmt.run(sleepTime, wakeTime, date);
// };

// export const getSleepRecords = () => {
//   const stmt = db.prepare('SELECT * FROM sleep_records ORDER BY date DESC');
//   return stmt.all();
// };
