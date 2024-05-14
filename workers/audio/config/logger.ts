import { createLogger, format, transports, Logger, addColors, LoggerOptions } from "winston"


const colors = {
    error: "red",
    warn: "yellow",
    info: "blue",
    verbose: "cyan",
    debug: "green",
    silly: "magenta"
}

const config = {
    levels: {
        error: 0,
        warn: 1,
        info: 2,
        verbose: 3,
        debug: 4,
        silly: 5
    },
    colors
}

addColors(colors)

const transport = process.env.NODE_ENV === "development" ? new transports.Console() : new transports.File({ filename: "logs/app.log" })

const struct = format.combine(
    format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
    format.align(),
    format.colorize({ all: true }),
    format.printf((info) => `${info.timestamp} ${info.level}: ${info.message}`)
)


const logger: Logger = createLogger({
    level: "debug",
    levels: config.levels,
    format: struct,
    transports: [transport],
    exitOnError: false
})

export { logger }