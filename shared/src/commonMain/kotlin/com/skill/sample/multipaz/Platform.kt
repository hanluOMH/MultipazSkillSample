package com.skill.sample.multipaz

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform