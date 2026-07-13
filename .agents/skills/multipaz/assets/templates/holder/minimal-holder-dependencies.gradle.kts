// Reference: references/dependency-guide.md
// Version-aware snippet only. Match the target project's existing dependency style.

dependencies {
    implementation("org.multipaz:multipaz:<multipaz-version>")
    implementation("org.multipaz:multipaz-doctypes:<multipaz-version>")
}

// Add these only when the workflow requires them:
// implementation("org.multipaz:multipaz-compose:<multipaz-version>")
// implementation("org.multipaz:multipaz-openid4vci:<multipaz-version>")
// implementation("org.multipaz:multipaz-dcapi:<multipaz-version>")
