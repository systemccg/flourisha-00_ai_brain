#!/bin/bash

#############################################################################
# New Project Creator
#
# Creates a new project from templates with PARA organization
# Location: /root/flourisha/00_AI_Brain/scripts/projects/new_project.sh
#
# Usage:
#   ./new_project.sh                    # Interactive mode
#   ./new_project.sh --help             # Show help
#
# Created: 2025-11-20
#############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
TEMPLATES_DIR="/root/flourisha/03f_Flourisha_Resources/Project_Templates"
PROJECTS_DIR="/root/flourisha/01f_Flourisha_Projects"
CURRENT_DATE=$(date +"%Y-%m-%d")

# Functions

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║      Flourisha Project Creator            ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

show_help() {
    cat << EOF
Flourisha Project Creator

Creates a new project from templates following PARA methodology.

USAGE:
    ./new_project.sh [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -t, --template TYPE     Template type (client|research|development|general)
    -n, --name NAME         Project name
    -q, --quick             Quick mode (skip optional questions)

EXAMPLES:
    ./new_project.sh                                # Interactive mode
    ./new_project.sh -t client -n "Acme Corp"      # Quick client project
    ./new_project.sh -t research -n "Market Analysis"

TEMPLATES:
    client          Client work, consulting, service delivery
    research        Research projects, analysis, investigations
    development     Software development, technical projects
    general         General purpose project

LOCATION:
    Projects are created in: $PROJECTS_DIR

EOF
}

# Check if templates directory exists
check_prerequisites() {
    if [ ! -d "$TEMPLATES_DIR" ]; then
        print_error "Templates directory not found: $TEMPLATES_DIR"
        exit 1
    fi

    if [ ! -d "$PROJECTS_DIR" ]; then
        print_error "Projects directory not found: $PROJECTS_DIR"
        exit 1
    fi
}

# List available templates
list_templates() {
    echo -e "${BLUE}Available Templates:${NC}"
    echo ""
    echo "  1) client       - Client projects and consulting"
    echo "  2) research     - Research and analysis projects"
    echo "  3) development  - Software development projects"
    echo "  4) general      - General purpose projects"
    echo ""
}

# Get template choice
get_template() {
    if [ -n "$TEMPLATE_TYPE" ]; then
        echo "$TEMPLATE_TYPE"
        return
    fi

    list_templates

    while true; do
        read -p "Select template (1-4 or name): " choice

        case $choice in
            1|client|client-project)
                echo "client-project"
                return
                ;;
            2|research|research-project)
                echo "research-project"
                return
                ;;
            3|development|development-project)
                echo "development-project"
                return
                ;;
            4|general|general-project)
                echo "general-project"
                return
                ;;
            *)
                print_error "Invalid choice. Please select 1-4 or enter template name."
                ;;
        esac
    done
}

# Get project name
get_project_name() {
    if [ -n "$PROJECT_NAME" ]; then
        echo "$PROJECT_NAME"
        return
    fi

    while true; do
        read -p "Enter project name: " name

        if [ -z "$name" ]; then
            print_error "Project name cannot be empty"
            continue
        fi

        # Check if project already exists
        if [ -d "$PROJECTS_DIR/$name" ]; then
            print_error "Project '$name' already exists"
            read -p "Choose different name? (y/n): " retry
            if [ "$retry" != "y" ]; then
                exit 1
            fi
            continue
        fi

        echo "$name"
        return
    done
}

# Sanitize folder name
sanitize_folder_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g' | sed 's/[^a-z0-9-]//g'
}

# Replace placeholders in files
replace_placeholders() {
    local project_dir="$1"
    local project_name="$2"
    local folder_name="$3"

    print_info "Customizing template files..."

    # Find all markdown files and replace placeholders
    find "$project_dir" -type f -name "*.md" | while read -r file; do
        sed -i "s/\[PROJECT NAME\]/$project_name/g" "$file"
        sed -i "s/\[CLIENT NAME\]/$project_name/g" "$file"
        sed -i "s/\[RESEARCH PROJECT NAME\]/$project_name/g" "$file"
        sed -i "s/\[DEVELOPMENT PROJECT NAME\]/$project_name/g" "$file"
        sed -i "s/\[DATE\]/$CURRENT_DATE/g" "$file"
    done

    print_success "Template customized"
}

# Create project from template
create_project() {
    local template="$1"
    local project_name="$2"
    local folder_name="$3"

    local template_path="$TEMPLATES_DIR/$template"
    local project_path="$PROJECTS_DIR/$folder_name"

    print_info "Creating project from $template template..."

    # Copy template to projects directory
    if ! cp -r "$template_path" "$project_path"; then
        print_error "Failed to create project"
        exit 1
    fi

    print_success "Project structure created"

    # Replace placeholders
    replace_placeholders "$project_path" "$project_name" "$folder_name"

    return 0
}

# Initialize git repo (optional)
init_git() {
    local project_path="$1"

    if [ "$QUICK_MODE" = true ]; then
        return
    fi

    read -p "Initialize git repository? (y/n): " git_init

    if [ "$git_init" = "y" ]; then
        print_info "Initializing git repository..."
        cd "$project_path" || exit
        git init > /dev/null 2>&1

        # Create .gitignore
        cat > .gitignore << 'GITEOF'
# OS
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Temp files
*.tmp
~$*

# Project specific
.env
secrets/
GITEOF

        git add .
        git commit -m "Initial commit: Project setup from template" > /dev/null 2>&1
        print_success "Git repository initialized"
    fi
}

# Sync to Google Drive
sync_to_drive() {
    if [ "$QUICK_MODE" = true ]; then
        print_info "Skipping Google Drive sync (quick mode)"
        return
    fi

    read -p "Sync to Google Drive now? (y/n): " sync_now

    if [ "$sync_now" = "y" ]; then
        print_info "Syncing to Google Drive..."
        if bash /root/.claude/scripts/flourisha_bisync.sh; then
            print_success "Synced to Google Drive"
        else
            print_error "Sync failed - run 'flourisha-bisync' manually later"
        fi
    else
        print_info "Remember to run 'flourisha-bisync' to sync to Google Drive"
    fi
}

# Show project summary
show_summary() {
    local project_path="$1"
    local project_name="$2"

    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Project Created Successfully!            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Project:${NC} $project_name"
    echo -e "${BLUE}Location:${NC} $project_path"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. cd $project_path"
    echo "  2. Review and customize README.md"
    echo "  3. Start working on your project"
    echo "  4. Run 'flourisha-bisync' to sync to Google Drive (if not done)"
    echo ""
    echo -e "${YELLOW}Files Created:${NC}"
    tree -L 1 "$project_path" 2>/dev/null || ls -la "$project_path"
    echo ""
}

# Main function
main() {
    print_header

    # Check prerequisites
    check_prerequisites

    # Get template
    local template=$(get_template)
    print_success "Template: $template"

    # Get project name
    local project_name=$(get_project_name)
    local folder_name=$(sanitize_folder_name "$project_name")
    print_success "Project name: $project_name"
    print_info "Folder name: $folder_name"
    echo ""

    # Create project
    create_project "$template" "$project_name" "$folder_name"

    local project_path="$PROJECTS_DIR/$folder_name"

    # Optional: Init git
    init_git "$project_path"

    # Optional: Sync to Google Drive
    sync_to_drive

    # Show summary
    show_summary "$project_path" "$project_name"
}

# Parse arguments
TEMPLATE_TYPE=""
PROJECT_NAME=""
QUICK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--template)
            TEMPLATE_TYPE="$2"
            shift 2
            ;;
        -n|--name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -q|--quick)
            QUICK_MODE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main
