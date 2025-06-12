# Sample Test Conversations

## 1. General Query Conversation

```
User: What services do you provide?
Bot: We offer a range of professional consultation services including business advisory, technical support, and personal coaching. Our experts are available for both virtual and telephonic appointments. You can book an appointment at your convenience, and we'll match you with the right specialist for your needs.

User: How long are the appointments?
Bot: Our standard appointments are 30 minutes long. However, if you need more time, you can request an extended session of 60 minutes when booking. For complex matters, we recommend booking an extended session to ensure we can address all your concerns thoroughly.

User: Thank you for the information
Bot: You're welcome! If you have any other questions or would like to book an appointment, feel free to let me know. I'm here to help you navigate our services.
```

## 2. Complete Appointment Booking Flow

```
Bot: Hi there! 
User: hi 

Bot: Could you please specify the date and time? 
User: Friday 1PM Bot: Got it. Noted your preference for Friday 01:00 PM. 

Bot: Do you prefer a Virtual or Telephonic appointment? 
User: virtual 

Bot: Confirming your Virtual appointment for Friday 01:00 PM. 
Debug: Loaded existing Excel file with 2 records 
Debug: Saved Excel file with 3 records 

Bot: Your appointment has been saved.
```

## 3. Edge Case - Missing Time

```
Bot: Hello!
hi

Bot: Could you please specify the date and time? For example, 'Monday at 3 PM' or 'next Friday at 10 AM'.
User: Monday

Bot: I see you've specified a day, but what time would you prefer?
User: Monday at 2PM

Bot: Got it. Noted your preference for Monday 02:00 PM.

Bot: Do you prefer a Virtual or Telephonic appointment?
User: telephonic

Bot: Confirming your Telephonic appointment for Monday 02:00 PM.
Debug: Loaded existing Excel file with 5 records
UserWarning: Could not infer format, so each element will be parsed individually, falling back to `dateutil`. To ensure parsing is consistent and as-expected, please specify a format.
  df["DateForSort"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors='coerce')
Debug: Saved Excel file with 6 records

Bot: Your appointment has been saved.
```

## 4. Edge Case - Time Conflict

```
Bot: Hi there!
hi

Bot: Could you please specify the date and time? For example, 'Monday at 3 PM' or 'next Friday at 10 AM'.
User: Monday 2PM

Bot: Got it. Noted your preference for Monday 02:00 PM.

Bot: Do you prefer a Virtual or Telephonic appointment?
User: virtual

Bot: Confirming your Virtual appointment for Monday 02:00 PM.
Debug: Loaded existing Excel file with 6 records

Bot: Sorry, Monday 02:00 PM is already booked. Please choose another time.

Bot: What other date and time would work for you?
User: Monday 3PM

Bot: Got it. Updated your preference to Monday 03:00 PM.

Bot: Got it. Noted your preference for Monday 03:00 PM.

Bot: Do you prefer a Virtual or Telephonic appointment?
User: virtual

Bot: Confirming your Virtual appointment for Monday 03:00 PM.
Debug: Loaded existing Excel file with 6 records
UserWarning: Could not infer format, so each element will be parsed individually, falling back to `dateutil`. To ensure parsing is consistent and as-expected, please specify a format.
  df["DateForSort"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors='coerce')
Debug: Saved Excel file with 7 records

Bot: Your appointment has been saved.
```

## 5. Edge Case - Complex Time Expression

```
Bot: Hi there!
hi

Bot: Could you please specify the date and time? For example, 'Monday at 3 PM' or 'next Friday at 10 AM'.
User: I need to talk to someone the day after tomorrow in the afternoon

Bot: Got it. Noted your preference for Saturday 03:00 PM.

Bot: Do you prefer a Virtual or Telephonic appointment?
User: virtual

Bot: Confirming your Virtual appointment for Saturday 03:00 PM.
Debug: Loaded existing Excel file with 7 records
UserWarning: Could not infer format, so each element will be parsed individually, falling back to `dateutil`. To ensure parsing is consistent and as-expected, please specify a format.
  df["DateForSort"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors='coerce')
Debug: Saved Excel file with 8 records

Bot: Your appointment has been saved.
```