import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus


class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            # set the novel status to be Issued
            novel = frappe.get_doc("Novel", self.novel)
            novel.status = "Issued"
            novel.save()

        elif self.type == "Return":
            self.validate_return()
            # set the novel status to be Available
            novel = frappe.get_doc("Novel", self.novel)
            novel.status = "Available"
            novel.save()

    def validate_issue(self):
        self.validate_membership()
        novel = frappe.get_doc("Novel", self.novel)
        # novel cannot be issued if it is already issued
        if novel.status == "Issued":
            frappe.throw("Novel is already issued by another member")

    def validate_return(self):
        novel = frappe.get_doc("Novel", self.novel)
        # novel cannot be returned if it is not issued first
        if novel.status == "Available":
            frappe.throw("Novel cannot be returned without being issued first")

    def validate_membership(self):
        # check if a valid membership exist for this library member
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<", self.date),
                "to_date": (">", self.date),
            },
        )
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")
