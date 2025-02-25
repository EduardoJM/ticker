'use strict';
{
    const $ = django.jQuery;

    $.fn.djangoAdminSelect2Dependencies = function() {
        $.each(this, function(i, element) {
            $(element).select2({
                ajax: {
                    data: (params) => {
                        const searchParams = new URLSearchParams(window.location.search);
                        const dependents = JSON.parse(element.dataset.dependencies);

                        const items = {
                            term: params.term,
                            page: params.page,
                            app_label: element.dataset.appLabel,
                            model_name: element.dataset.modelName,
                            field_name: element.dataset.fieldName
                        }
                        for (const dep of dependents) {
                            if (searchParams.get(dep)) {
                                const param = dep.replace(element.dataset.fieldPath + '__', '');
                                items[param] = searchParams.get(dep);
                            }
                        }

                        return items;
                    }
                }
            });
        });
        return this;
    };

    $(function() {
        // Initialize all autocomplete widgets except the one in the template
        // form used when a new formset is added.
        $('.admin-autocompleterelated').not('[name*=__prefix__]').djangoAdminSelect2Dependencies();
    });

    document.addEventListener('formset:added', (event) => {
        $(event.target).find('.admin-autocompleterelated').djangoAdminSelect2Dependencies();
    });
}