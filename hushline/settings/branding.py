from typing import Tuple

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    render_template,
    request,
    session,
)

from hushline.auth import admin_authentication_required
from hushline.db import db
from hushline.model import (
    OrganizationSetting,
    User,
)
from hushline.settings.common import (
    form_error,
)
from hushline.settings.forms import (
    DeleteBrandLogoForm,
    SetHomepageUsernameForm,
    UpdateBrandAppNameForm,
    UpdateBrandLogoForm,
    UpdateBrandPrimaryColorForm,
    UpdateDirectoryTextForm,
)
from hushline.storage import public_store


def register_branding_routes(bp: Blueprint) -> None:
    @bp.route("/branding", methods=["GET", "POST"])
    @admin_authentication_required
    def branding() -> Tuple[str, int]:
        user = db.session.scalars(db.select(User).filter_by(id=session["user_id"])).one()

        update_directory_text_form = UpdateDirectoryTextForm(
            markdown=OrganizationSetting.fetch_one(OrganizationSetting.DIRECTORY_INTRO_TEXT)
        )
        update_brand_logo_form = UpdateBrandLogoForm()
        delete_brand_logo_form = DeleteBrandLogoForm()
        update_brand_primary_color_form = UpdateBrandPrimaryColorForm()
        update_brand_app_name_form = UpdateBrandAppNameForm()
        set_homepage_username_form = SetHomepageUsernameForm(
            username=OrganizationSetting.fetch_one(OrganizationSetting.HOMEPAGE_USER_NAME)
        )

        status_code = 200
        if request.method == "POST":
            if (
                update_directory_text_form.submit.name in request.form
                and update_directory_text_form.validate()
            ):
                if md := update_directory_text_form.markdown.data.strip():
                    OrganizationSetting.upsert(
                        key=OrganizationSetting.DIRECTORY_INTRO_TEXT, value=md
                    )
                    db.session.commit()
                    flash("👍 Directory intro text updated")
                else:
                    row_count = db.session.execute(
                        db.delete(OrganizationSetting).where(
                            OrganizationSetting.key == OrganizationSetting.DIRECTORY_INTRO_TEXT
                        )
                    ).rowcount
                    if row_count > 1:
                        current_app.logger.error(
                            "Would have deleted multiple rows for OrganizationSetting key="
                            + OrganizationSetting.DIRECTORY_INTRO_TEXT
                        )
                        db.session.rollback()
                        abort(503)
                    db.session.commit()
                    flash("👍 Directory intro text was reset to defaults")
            elif (
                update_brand_logo_form.submit.name in request.form
                and update_brand_logo_form.validate()
            ):
                public_store.put(
                    OrganizationSetting.BRAND_LOGO_VALUE, update_brand_logo_form.logo.data
                )
                OrganizationSetting.upsert(
                    key=OrganizationSetting.BRAND_LOGO,
                    value=OrganizationSetting.BRAND_LOGO_VALUE,
                )
                db.session.commit()
                flash("👍 Brand logo updated successfully.")
            elif (
                delete_brand_logo_form.submit.name in request.form
                and delete_brand_logo_form.validate()
            ):
                row_count = db.session.execute(
                    db.delete(OrganizationSetting).where(
                        OrganizationSetting.key == OrganizationSetting.BRAND_LOGO
                    )
                ).rowcount
                if row_count > 1:
                    current_app.logger.error(
                        "Would have deleted multiple rows for OrganizationSetting key="
                        + OrganizationSetting.BRAND_LOGO
                    )
                    db.session.rollback()
                    abort(503)
                db.session.commit()
                public_store.delete(OrganizationSetting.BRAND_LOGO_VALUE)
                flash("👍 Brand logo deleted.")
            elif (
                update_brand_primary_color_form.submit.name in request.form
                and update_brand_primary_color_form.validate()
            ):
                OrganizationSetting.upsert(
                    key=OrganizationSetting.BRAND_PRIMARY_COLOR,
                    value=update_brand_primary_color_form.brand_primary_hex_color.data,
                )
                db.session.commit()
                flash("👍 Brand primary color updated successfully.")
            elif (
                update_brand_app_name_form.submit.name in request.form
                and update_brand_app_name_form.validate()
            ):
                OrganizationSetting.upsert(
                    key=OrganizationSetting.BRAND_NAME,
                    value=update_brand_app_name_form.brand_app_name.data,
                )
                db.session.commit()
                flash("👍 Brand app name updated successfully.")
            elif set_homepage_username_form.delete_submit.name in request.form:
                row_count = db.session.execute(
                    db.delete(OrganizationSetting).filter_by(
                        key=OrganizationSetting.HOMEPAGE_USER_NAME
                    )
                ).rowcount
                match row_count:
                    case 0:
                        flash("👍 Homepage reset to default")
                    case 1:
                        db.session.commit()
                        set_homepage_username_form.username.data = None
                        flash("👍 Homepage reset to default")
                    case _:
                        current_app.logger.error(
                            f"Deleting OrganizationSetting {OrganizationSetting.HOMEPAGE_USER_NAME}"
                            " would have deleted multiple rows"
                        )
                        status_code = 500
                        db.session.rollback()
                        flash("There was an error and the setting could not reset")
            elif (
                set_homepage_username_form.submit.name in request.form
                and set_homepage_username_form.validate()
            ):
                OrganizationSetting.upsert(
                    key=OrganizationSetting.HOMEPAGE_USER_NAME,
                    value=set_homepage_username_form.username.data,
                )
                db.session.commit()
                flash(f"👍 Homepage set to user {set_homepage_username_form.username.data!r}")
            else:
                form_error()
                status_code = 400

        return render_template(
            "settings/branding.html",
            user=user,
            update_directory_text_form=update_directory_text_form,
            update_brand_logo_form=update_brand_logo_form,
            delete_brand_logo_form=delete_brand_logo_form,
            update_brand_primary_color_form=update_brand_primary_color_form,
            update_brand_app_name_form=update_brand_app_name_form,
            set_homepage_username_form=set_homepage_username_form,
        ), status_code
