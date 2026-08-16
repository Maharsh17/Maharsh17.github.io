#!/usr/bin/env bash
# Regenerates combined-gta/data/projects.json from the GitHub API.
# Safe to rerun. Never edit the output by hand; edit overrides.json instead.
set -euo pipefail
cd "$(dirname "$0")/.."

REPOS='["InviteInstitute/lm-dashboard","InviteInstitute/vex-agent-integration","InviteInstitute/agent-lm-packages","Maharsh17/county-clustering","CS222-UIUC/fa25-team118-titans","Maharsh17/resume-blaster","HarshithaS2023/ai4all"]'

gh api graphql -f query='
{
  viewer {
    repositories(first:100, ownerAffiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER]) {
      nodes {
        nameWithOwner isPrivate isArchived pushedAt description
        releases { totalCount }
        languages(first:8, orderBy:{field:SIZE,direction:DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}' | jq --argjson want "$REPOS" '{
  generated: (now | strftime("%Y-%m-%d")),
  repos: [
    .data.viewer.repositories.nodes[]
    | select(.nameWithOwner as $n | $want | index($n))
    | {
        nameWithOwner,
        pushedAt: .pushedAt[0:10],
        isPrivate,
        isArchived,
        description,
        releaseCount: .releases.totalCount,
        languages: [.languages.edges[] | {name: .node.name, size: .size}]
      }
  ]
}' > combined-gta/data/projects.json

echo "wrote combined-gta/data/projects.json ($(jq '.repos|length' combined-gta/data/projects.json) repos)"
