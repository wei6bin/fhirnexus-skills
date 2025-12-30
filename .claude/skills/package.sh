#!/bin/bash
# Package FHIR Engine Claude Skills for distribution

set -e

VERSION=$(head -n 1 VERSION)
PACKAGE_NAME="fhir-engine-claude-skills-v${VERSION}"
OUTPUT_DIR="../../dist"

echo "Packaging FHIR Engine Claude Skills v${VERSION}"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="${TEMP_DIR}/${PACKAGE_NAME}"
mkdir -p "${PACKAGE_DIR}"

# Copy skill directories
echo "Copying skills..."
cp -r fhir-config-troubleshooting "${PACKAGE_DIR}/"
cp -r handler-patterns "${PACKAGE_DIR}/"
cp -r fhir-errors-debugger "${PACKAGE_DIR}/"

# Copy documentation
echo "Copying documentation..."
cp README.md "${PACKAGE_DIR}/"
cp GETTING_STARTED.md "${PACKAGE_DIR}/"
cp DISTRIBUTION.md "${PACKAGE_DIR}/"
cp LICENSE "${PACKAGE_DIR}/"
cp VERSION "${PACKAGE_DIR}/"

# Copy package README as main README
cp PACKAGE_README.md "${PACKAGE_DIR}/README.md"

# Create installation script
cat > "${PACKAGE_DIR}/install.sh" << 'EOF'
#!/bin/bash
# Install FHIR Engine Claude Skills

INSTALL_DIR="${1:-.claude/skills}"

echo "Installing FHIR Engine Claude Skills to ${INSTALL_DIR}"

# Create target directory
mkdir -p "${INSTALL_DIR}"

# Copy skills
cp -r fhir-config-troubleshooting "${INSTALL_DIR}/"
cp -r handler-patterns "${INSTALL_DIR}/"
cp -r fhir-errors-debugger "${INSTALL_DIR}/"

echo "✓ Skills installed successfully!"
echo ""
echo "Next steps:"
echo "1. Open your FHIR API project in Claude Code"
echo "2. Ask: 'What skills are available?'"
echo "3. Start building: 'How do I create a Patient handler?'"
EOF

chmod +x "${PACKAGE_DIR}/install.sh"

# Create ZIP archive
echo "Creating ZIP archive..."
cd "${TEMP_DIR}"
zip -r "${OUTPUT_DIR}/${PACKAGE_NAME}.zip" "${PACKAGE_NAME}"

# Create tar.gz archive
echo "Creating tar.gz archive..."
tar -czf "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

# Cleanup
rm -rf "${TEMP_DIR}"

echo ""
echo "✓ Packaging complete!"
echo ""
echo "Created packages:"
echo "  ${OUTPUT_DIR}/${PACKAGE_NAME}.zip"
echo "  ${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz"
echo ""
echo "Distribution options:"
echo "  1. Upload to documentation site"
echo "  2. Include in NuGet package content"
echo "  3. Publish to GitHub releases"
echo "  4. Share with developers directly"
echo ""
echo "See DISTRIBUTION.md for detailed distribution strategies."
