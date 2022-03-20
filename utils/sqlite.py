import aiosqlite
import utils.logger


async def setup_db(filepath: str = "./db/database.db"):
    """
    Sets up the database with the required tables.
    Only really needed for first-time setup, or when we add a table.
    """
    async with aiosqlite.connect(filepath) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS warnings(
                user_id INTEGER,
                warn_id INTEGER,
                mod_id INTEGER,
                reason TEXT,
                timestamp TEXT)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS starboardmessages(
                original_id INTEGER,
                starboard_id INTEGER)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS reminder(
                user_id INTEGER,
                reminder_id INTEGER,
                channel_id INTEGER,
                date INTEGER,
                read_time TEXT,
                message TEXT)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS reactrole(
                message_id INTEGER,
                exclusive INTEGER,
                rolereq TEXT,
                emoji TEXT,
                role INTEGER)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS ranking(
                user_id INTEGER,
                wins INTEGER,
                losses INTEGER,
                elo INTEGER,
                matches TEXT)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS profile(
                user_id INTEGER,
                tag TEXT,
                region TEXT,
                mains TEXT,
                secondaries TEXT,
                pockets TEXT,
                note TEXT,
                colour INTEGER)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS muted(
                user_id INTEGER,
                muted INTEGER)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS macros(
                name TEXT,
                payload TEXT)"""
        )

        await db.execute(
            """CREATE TABLE IF NOT EXISTS userbadges(
            user_id INTEGER,
            badges TEXT)"""
        )

        await db.commit()

        logger = utils.logger.get_logger("bot.db")
        logger.info("Database setup complete!")
