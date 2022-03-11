#!/usr/bin/env python3

import argparse

from os import environ
from snyk import SnykClient
from snyk.models import Organization, Project

# todo - enable logger for everything and figure out how to pass debug statements to requests


def parse_command_line_args():
    parser = argparse.ArgumentParser(
        description="Generate a CSV of projects in a Snyk Organization"
    )
    parser.add_argument(
        "--org-id",
        help="The organization ID from the Org's Setting panel",
        required=True,
    )
    parser.add_argument(
        "--integration",
        help="Integration Name: bitbucket-cloud, github-enterprise, etc.",
    )
    parser.add_argument(
        "--attribute",
        help="Which target attribute to tag the projects with",
    )
    parser.add_argument(
        "--field-sep",
        help="Optional field separator",
    )
    parser.add_argument(
        "--field-num",
        help="Which field to use",
    )
    parser.add_argument(
        "--tag-name",
        help="What is the tag's Key name, attribute value is used by default",
    )
    parser.add_argument(
        "--strip-char",
        help="Remove this character from the beginning the field if it is present",
    )

    return parser.parse_args()


def update_tag(project: dict, v1_org: Organization) -> bool:

    live_tags = project["tags"]

    needs_removed = list()

    tag_update = True

    for tag in live_tags:
        if tag["key"] == project["tag_name"]:
            if tag["value"] == project["tag_value"]:
                # tag already exists and matches
                tag_update = False
                print(f"tag {tag['key']}:{tag['value']} exists")
            else:
                # this has the same name but wrong value add to remove pile
                print(f"tag {tag['key']}:{tag['value']} needs removed")
                needs_removed.append(tag)

    if len(needs_removed) > 0 or tag_update:

        live_p: Project = v1_org.projects.get(project["snyk_id"])

        for tag in needs_removed:
            print("removing tag")
            live_p.tags.delete(tag["key"], tag["value"])

        if tag_update:
            live_p.tags.add(project["tag_name"], project["tag_value"])

    return


def f_strip(tag_value, strip_char) -> str:
    if tag_value[0] == strip_char:
        return tag_value[1:]
    else:
        return tag_value


if __name__ == "__main__":
    args = parse_command_line_args()
    org_id = args.org_id or "1b48e2c4-6ca8-455f-a73f-d2f6f2a6b225"
    int_name = args.integration or "all"
    attribute = args.attribute or f"name"
    field_sep = args.field_sep or None
    field_num = args.field_num or None
    tag_name = args.tag_name or None
    strip_char = args.strip_char or None

    print(field_num, field_sep)

    # "displayName": "snyk-fixtures/goof"
    #

    snyk_token = environ["SNYK_TOKEN"]

    if snyk_token == "BD832F91-A742-49E9-BC1E-411E0C8743EA":
        print("You didn't update example_secrets.sh with a valid token")
        exit(1)

    v1 = SnykClient(snyk_token)
    v3 = SnykClient(
        snyk_token, version="2022-02-16~experimental", url="https://api.snyk.io/v3"
    )

    v1_org = v1.organizations.get(org_id)

    t_params = {"origin": int_name, "limit": 100}

    all_targets = v3.get_v3_pages(f"orgs/{org_id}/targets", t_params)

    # now we need to filter all our targets since the response will be a list objects formated like this:
    # {
    #     "attributes": {
    #         "displayName": "snyk-fixtures/goof",
    #         "isPrivate": False,
    #         "origin": "github",
    #         "remoteUrl": "http://github.com/snyk/local-goof",
    #     },
    #     "id": "55a348e2-c3ad-4bbc-b40e-9b232d1f4121",
    #     "relationships": {
    #         "org": {
    #             "data": {"id": "e661d4ef-5ad5-4cef-ad16-5157cefa83f5", "type": "org"},
    #             "links": {
    #                 "self": {"href": "/v3/orgs/e661d4ef-5ad5-4cef-ad16-5157cefa83f5"}
    #             },
    #         }
    #     },
    #     "type": "target",
    # }

    # lets make a new list

    compacted = list()

    # lets go through each element in the target response

    for target in all_targets:
        tmp_target = list()
        # copy the contents of attributes to a temporary target
        tmp_target = target["attributes"]

        # now tmp_target looks like this:
        #    {
        #         "displayName": "snyk-fixtures/goof",
        #         "isPrivate": False,
        #         "origin": "github",
        #         "remoteUrl": "http://github.com/snyk/local-goof",
        #     }

        # lets copy that id field also, which we need to access this target in the future
        # Targets api may return a field called id in the future in the attributes section
        # so lets be more specific and call this the snyk_id

        tmp_target["snyk_id"] = target["id"]

        # since compacted is a list, we can use its append() method to attach tmp_target to it

        compacted.append(tmp_target)

        # the next loop will reset the contents of tmp_target and start over with the next item in the all_targets list

    # if we're doing a basic split of the attribute value
    if field_num is not None and field_sep is not None:
        f_num = int(field_num)
        f_sep = str(field_sep)

        for target in compacted:
            try:
                tag_value = str(target[attribute]).split(f_sep)[f_num]
                tag_value = tag_value.lower()
            except Exception:
                break

            target["tag_value"] = f_strip(tag_value, strip_char)
    else:
        for target in compacted:
            tag_value = str(target[attribute]).lower()
            target["tag_value"] = f_strip(tag_value, strip_char)

    compacted = [t for t in compacted if "tag_value" in t.keys()]

    all_projects = list()

    for target in compacted:
        p_params = {"origin": int_name, "targetId": target["snyk_id"], "limit": 100}

        t_projects = v3.get_all_pages(f"/orgs/{org_id}/projects", p_params)

        for p in t_projects:

            tmp_p = {
                "snyk_id": p["id"],
                "tag_name": tag_name or attribute,
                "tag_value": target["tag_value"],
                "tags": p["attributes"]["tags"],
            }

            all_projects.append(tmp_p)

    print(all_projects)
    for p in all_projects:
        update_tag(p, v1_org)
