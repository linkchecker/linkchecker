Contribution Guide
==================

This document outlines how to contribute to this project. It details
instructions on how to submit issues, bug reports and patches.

Before you participate in the community, you should also agree to
respect the code of conduct, shipped in
:doc:`CODE_OF_CONDUCT.rst <code_of_conduct>` in the source code.

Positive feedback
-----------------

Even if you have no changes, suggestions, documentation or bug reports
to submit, even just positive feedback like “it works” goes a long way.
It shows the project is being used and gives instant gratification to
contributors. So we welcome emails that tell us of your positive
experiences with the project or just thank you notes. Contact
maintainers directly or submit a closed issue with your story. You can
also send your “thanks” through https://saythanks.io/.

Issues and bug reports
----------------------

We want you to report issues you find in the software. It is a
recognized and important part of contributing to this project. All
issues will be read and replied to politely and professionally. Issues
and bug reports should be filed on the `issue
tracker <https://github.com/linkchecker/linkchecker/issues>`__.

Issue triage
^^^^^^^^^^^^

Issue triage is a useful contribution as well. You can review the
`issues <https://github.com/linkchecker/linkchecker/issues>`__ in the
`project page <https://github.com/linkchecker/linkchecker/>`__ and, for
each issue:

-  try to reproduce the issue, if it is not reproducible, label it with
   ``help-wanted`` and explain the steps taken to reproduce
-  if information is missing, label it with ``invalid`` and request
   specific information
-  if the feature request is not within the scope of the project or
   should be refused for other reasons, use the ``wontfix`` label and
   close the issue
-  mark feature requests with the ``enhancement`` label, bugs with
   ``bug``, duplicates with ``duplicate`` and so on…

Note that some of those operations are available only to project
maintainers, see below for the different statuses.

Security issues
^^^^^^^^^^^^^^^

Security issues should first be disclosed privately to the project
maintainers, which support receiving encrypted emails through the usual
OpenPGP key discovery mechanisms.

This project cannot currently afford bounties for security issues. We
would still ask that you coordinate disclosure, giving the project a
reasonable delay to produce a fix and prepare a release before public
disclosure.

Public recognition will be given to reporters security issues if
desired. We otherwise agree with the `Disclosure
Guidelines <https://www.hackerone.com/disclosure-guidelines>`__ of the
`HackerOne project <https://www.hackerone.com/>`__, at the time of
writing.

Patches
-------

Patches can be submitted through `pull
requests <https://github.com/linkchecker/linkchecker/pulls>`__ on the
`project page <https://github.com/linkchecker/linkchecker/>`__.

Some guidelines for patches:

-  A patch should be a minimal and accurate answer to exactly one
   identified and agreed problem.
-  A patch must compile cleanly and pass project self-tests on all
   target platforms.
-  A patch commit message must consist of a single short (less than 50
   characters) line stating a summary of the change, followed by a blank
   line and then a description of the problem being solved and its
   solution, or a reason for the change. Write more information, not
   less, in the commit log.
-  Patches should be reviewed by at least one maintainer before being
   merged.

Project maintainers should merge their own patches only when they have
been approved by other maintainers, unless there is no response within a
reasonable timeframe (roughly one week) or there is an urgent change to
be done (e.g. security or data loss issue).

As an exception to this rule, this specific document cannot be changed
without the consensus of all administrators of the project.

   Note: Those guidelines were inspired by the `Collective Code
   Construction Contract <https://rfc.zeromq.org/spec/42/>`__. The
   document was found to be a little too complex and hard to read and
   wasn’t adopted in its entirety. See this
   `discussion <https://github.com/zeromq/rfc/issues?utf8=%E2%9C%93&q=author%3Aanarcat%20>`__
   for more information.

Patch triage
^^^^^^^^^^^^

You can also review existing pull requests, by cloning the contributor’s
repository and testing it. If the tests do not pass (either locally or
in Travis), if the patch is incomplete or otherwise does not respect the
above guidelines, submit a review with “changes requested” with
reasoning.

Membership
----------

There are three levels of membership in the project, Administrator (also
known as “Owner” in GitHub), Maintainer (also known as “Member”), or
regular users (everyone with or without a GitHub account). Anyone is
welcome to contribute to the project within the guidelines outlined in
this document, regardless of their status, and that includes regular
users.

Maintainers can:

-  do everything regular users can
-  review, push and merge pull requests
-  edit and close issues

Administrators can:

-  do everything maintainers can
-  add new maintainers
-  promote maintainers to administrators

Regular users can be promoted to maintainers if they contribute to the
project, either by participating in issues, documentation or pull
requests.

Maintainers can be promoted to administrators when they have given
significant contributions for a sustained timeframe, by consensus of the
current administrators. This process should be open and decided as any
other issue.

Maintainers can be demoted by administrators and administrators can be
demoted by the other administrators’ consensus. Unresponsive maintainers
or administrators can be removed after a month unless they specifically
announced a leave.
