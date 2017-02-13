This document outlines how to contribute to this project. It details a
code of conduct, how to submit issues, bug reports and patches.

# Contributor Covenant Code of Conduct

## Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

## Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

## Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting one of the persons listed below. All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. The project maintainers is
obligated to maintain confidentiality with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

Project maintainers are encouraged to follow the spirit of the
[Django Code of Conduct Enforcement Manual][enforcement] when
receiving reports.

 [enforcement]: https://www.djangoproject.com/conduct/enforcement-manual/

## Contacts

The following people have volunteered to be available to respond to
Code of Conduct reports. They have reviewed existing literature and
agree to follow the aforementioned process in good faith. They also
accept OpenPGP-encrypted email:

 * Antoine Beaupré <anarcat@debian.org>

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 1.4,
available at [http://contributor-covenant.org/version/1/4][version]

[homepage]: http://contributor-covenant.org
[version]: http://contributor-covenant.org/version/1/4/

Changes
-------

The Code of Conduct was modified to refer to *project maintainers*
instead of *project team* and small paragraph was added to refer to
the Django enforcement manual.

> Note: We have so far determined that writing an explicit enforcement
> policy is not necessary, considering the available literature
> already available online and the relatively small size of the
> community. This may change in the future if the community grows
> larger.

# Patches

Patches can be submitted through [pull requests][] on the
[GitHub project][].

[pull requests]: https://github.com/linkcheck/linkchecker/pulls
[GitHub project]: https://github.com/linkcheck/linkchecker

Some guidelines for patches:

* A patch should be a minimal and accurate answer to exactly one
  identified and agreed problem.
* A patch must compile cleanly and pass project self-tests on all
  target platforms.
* A patch commit message must consist of a single short (less than 50
  characters) line stating a summary of the change, followed by a
  blank line and then a description of the problem being solved and
  its solution, or a reason for the change. Write more information,
  not less, in the commit log.
* Patches should be reviewed by at least one maintainer before being merged.

Project maintainers should merge their own patches only when they have been
approved by other maintainers, unless there is no response within a
reasonable timeframe (roughly one week) or there is an urgent change
to be done (e.g. security or data loss issue).

As an exception to this rule, this specific document cannot be changed
without the consensus of all administrators of the project.

> Note: Those guidelines were inspired by the
> [Collective Code Construct Contract][C4]. The document was found to
> be a little too complex and hard to read and wasn't adopted in its
> entirety. See this [discussion][] for more information.

 [C4]: https://rfc.zeromq.org/spec:42/C4/
 [discussion]: https://github.com/zeromq/rfc/issues?utf8=%E2%9C%93&q=author%3Aanarcat%20

## Patch triage

You can also review existing pull requests, by cloning the
contributor's repository and testing it. If the tests do not pass
(either locally or in Travis), if the patch is incomplete or otherwise
does not respect the above guidelines, submit a review with "changes
requested" with reasoning.

# Issues and bug reports

We want you to report issuess you find in the software. It is a
recognized and important part of contributing to this project. All
issues will be read and replied to politely and
professionnally. Issues and bug reports should be filed on the
[GitHub issue tracker][issues].

## Issue triage

Issue triage is a useful contribution as well. You can review the
[issues][] in the GitHub project and, for each issue:

-  try to reproduce the issue, if it is not reproducible, label it with
   `help-wanted` and explain the steps taken to reproduce
-  if information is missing, label it with `invalid` and request
   specific information
-  if the feature request is not within the scope of the project or
   should be refused for other reasons, use the `wontfix` label and
   close the issue
-  mark feature requests with the `enhancement` label, bugs with
   `bug`, duplicates with `duplicate` and so on...

[issues]: https://github.com/linkcheck/linkchecker/issues

Note that some of those operations are available only to project
maintainers, see below for the different statuses.

# Membership

There are three levels of membership in the project, Administrator
(also known as "Owner" in GitHub), Maintainer (also known as
"Member"), or regular users (everyone with or without a GitHub
account). Anyone is welcome to contribute to the project within the
guidelines outlined in this document, regardless of their status, and
that includes regular users.

Maintainers can:

* do everything regular users can
* review, push and merge pull requests
* edit and close issues

Administrators can:

* do everything maintainers can
* add new maintainers
* promote maintainers to administrators

Regular users can be promoted to maintainers if they contribute to the
project, either by participating in issues, documentation or pull
requests.

Maintainers can be promoted to administrators when they have given significant
contributions for a sustained timeframe, by consensus of the current
administrators. This process should be open and decided as any other issue.
