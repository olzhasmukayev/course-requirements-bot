import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from src.utils import load_data, load_user_state, save_user_state
import pdfplumber
import io
import re

logger = logging.getLogger()
database, credits = load_data()
kazakh_keyboard = [["Basic", "Intermediate", "Advanced"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = await load_user_state(user_id)
    state["conversation_state"] = "TRANSCRIPT"
    await save_user_state(user_id, state)
    await update.message.reply_text("Please upload your unofficial transcript.")

async def handle_transcript(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = await load_user_state(user_id)
    
    if state.get("conversation_state") != "TRANSCRIPT":
        await update.message.reply_text("Please start by uploading your transcript using /start.")
        return

    file = update.message.document
    if file:
        try:
            file_object = await file.get_file()
            file_content = await file_object.download_as_bytearray()

            completed_courses = extract_courses_from_transcript(file_content)
            state["completed_courses"] = list(completed_courses)

            await update.message.reply_text(
                "Thank you! Your transcript has been processed successfully."
            )

            reply_markup = ReplyKeyboardMarkup(
                kazakh_keyboard, one_time_keyboard=True, resize_keyboard=True
            )
            await update.message.reply_text(
                "Please specify your Kazakh language level.", reply_markup=reply_markup
            )

            state["conversation_state"] = "KAZAKH_LEVEL"
            await save_user_state(user_id, state)

        except Exception as e:
            logger.error(f"Error processing transcript for user {user_id}: {e}")
            await update.message.reply_text("An error occurred while processing the file.")
    else:
        await update.message.reply_text("Please upload a valid transcript file.")

async def handle_kazakh_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    kazakh_level = update.message.text
    state = await load_user_state(user_id)

    if state.get("conversation_state") != "KAZAKH_LEVEL":
        await update.message.reply_text("Please upload your transcript before selecting your Kazakh level.")
        return

    if kazakh_level not in ["Basic", "Intermediate", "Advanced"]:
        await update.message.reply_text(
            "Please select a valid Kazakh language level.",
            reply_markup=ReplyKeyboardMarkup(kazakh_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return

    state["kazakh_level"] = kazakh_level
    await update.message.reply_text(f"You selected Kazakh level: {kazakh_level}.")

    reply_markup = ReplyKeyboardMarkup(
        [[major] for major in database.keys()], one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text("Please select your major.", reply_markup=reply_markup)

    state["conversation_state"] = "MAJOR"
    await save_user_state(user_id, state)

async def handle_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    major = update.message.text
    state = await load_user_state(user_id)

    if major not in database:
        await update.message.reply_text("Please select a valid major.")
        return

    state["major"] = major
    await update.message.reply_text(f"Your selected major: {major}")

    completed_courses = set(state.get("completed_courses", []))
    kazakh_level = state.get("kazakh_level")
    result_message = f"Major: {major}\nKazakh Level: {kazakh_level}\n"

    satisfied_courses = check_courses(completed_courses, major)
    result_message += f"Satisfied Courses: {', '.join(satisfied_courses)}"

    await update.message.reply_text(result_message)

    state.clear()
    await save_user_state(user_id, state)

def extract_courses_from_transcript(file_content: bytes) -> set:
    valid_grades = {"D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "P"}
    valid_courses = set()

    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            matches = re.findall(r"([A-Z]+\s\d{3}[A-Z]?).+([A-Z][+-]?)", text)
            for match in matches:
                course_code, grade = match
                if grade in valid_grades:
                    valid_courses.add(course_code)

    return valid_courses

def check_courses(completed_courses: set, major: str):
    major_courses = database[major]["major_courses"]
    return [course for course in major_courses if course in completed_courses]
