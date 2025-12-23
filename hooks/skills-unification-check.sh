#!/bin/bash

##############################################################################
# skills-unification-check.sh
#
# Git pre-commit hook to enforce skills unification strategy
# Prevents commits that add files directly to /root/.claude/skills/
# Warns about potential skill divergence
#
# Installation:
#   cp skills-unification-check.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
##############################################################################

set -e

CLAUDE_SKILLS="/root/.claude/skills"
FLOURISHA_SKILLS="/root/flourisha/00_AI_Brain/skills"

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

##############################################################################
# Check 1: Prevent commits to .claude/skills/ directory
##############################################################################

if git diff --cached --name-only 2>/dev/null | grep -q "^\.claude/skills/"; then
  echo -e "${RED}❌ ERROR: Attempted to commit files to .claude/skills/${NC}"
  echo ""
  echo -e "${YELLOW}WHY:${NC}"
  echo "  /root/.claude/skills/ is a symlink to /root/flourisha/00_AI_Brain/skills/"
  echo "  Committing to this path causes confusion and divergence risk."
  echo ""
  echo -e "${GREEN}SOLUTION:${NC}"
  echo "  All skills must be created/edited in:"
  echo "  /root/flourisha/00_AI_Brain/skills/"
  echo ""
  echo -e "${YELLOW}EXAMPLE:${NC}"
  echo "  # Create skill in the right place:"
  echo "  mkdir -p /root/flourisha/00_AI_Brain/skills/my-skill"
  echo "  nano /root/flourisha/00_AI_Brain/skills/my-skill/SKILL.md"
  echo "  git add flourisha/00_AI_Brain/skills/my-skill/"
  echo "  git commit -m 'Add my-skill'"
  echo ""
  exit 1
fi

##############################################################################
# Check 2: Warn about skill divergence
##############################################################################

DIVERGENCE_FOUND=0

if [ -d "$FLOURISHA_SKILLS" ]; then
  for skill_dir in "$FLOURISHA_SKILLS"/*; do
    # Skip if not a directory
    [ -d "$skill_dir" ] || continue

    skill_name=$(basename "$skill_dir")
    claude_path="$CLAUDE_SKILLS/$skill_name"

    # If same skill exists in both locations AND is NOT a symlink...
    if [ -d "$claude_path" ] && [ ! -L "$claude_path" ]; then
      # Check if they're different (ignoring hidden files and common differences)
      if ! diff -r \
        --exclude='.git' \
        --exclude='.DS_Store' \
        --exclude='__pycache__' \
        "$claude_path" "$skill_dir" >/dev/null 2>&1; then

        echo -e "${YELLOW}⚠️  WARNING: Skill '$skill_name' has diverged${NC}"
        echo "   Location 1: $CLAUDE_SKILLS/$skill_name"
        echo "   Location 2: $FLOURISHA_SKILLS/$skill_name"
        echo ""
        echo -e "${GREEN}TO FIX:${NC}"
        echo "   cp -r $skill_dir $claude_path"
        echo ""

        DIVERGENCE_FOUND=1
      fi
    fi
  done
fi

##############################################################################
# Check 3: Ensure all committed skills are in Flourisha location
##############################################################################

git diff --cached --name-only 2>/dev/null | grep "^flourisha/00_AI_Brain/skills/" | while read -r file; do
  # Extract skill name from path
  skill_name=$(echo "$file" | sed 's|flourisha/00_AI_Brain/skills/\([^/]*\)/.*|\1|')

  # Verify symlink exists
  if [ ! -L "$CLAUDE_SKILLS/$skill_name" ]; then
    # Check if it's an actual directory (bad - divergence risk)
    if [ -d "$CLAUDE_SKILLS/$skill_name" ]; then
      echo -e "${YELLOW}⚠️  WARNING: Skill '$skill_name' exists as real directory in .claude/skills/${NC}"
      echo ""
      echo "   This will cause divergence. Please clean up:"
      echo "   rm -rf $CLAUDE_SKILLS/$skill_name"
      echo ""
      DIVERGENCE_FOUND=1
    fi
  fi
done

##############################################################################
# Final Status
##############################################################################

if [ $DIVERGENCE_FOUND -eq 1 ]; then
  echo -e "${YELLOW}⚠️  Commit allowed but divergence detected. Recommended fixes above.${NC}"
  echo ""
fi

echo -e "${GREEN}✅ Skills unification check passed${NC}"
exit 0
