from . import msgFact as _
from .vocabularies import TEXT_IDX
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.portlets.browser import z3cformhelper
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize.instance import memoize
from plone.portlet.collection.collection import Renderer as CollectionRenderer
from plone.portlets.interfaces import IPortletDataProvider
from z3c.form import field
from zope import schema
from zope.interface import implements


class ICollectionSearchPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_('label_header', default=u'Portlet header'),
        description=_(
            'help_header'
            u'Title of the rendered portlet.'
        ),
        required=False,
    )

    target_collection = schema.Choice(
        title=_(u'label_target_collection', default=u'Target Collection'),
        description=_(
            u'help_target_collection',
            default=u'The collection, which is the source for the filter '
                    u'items and where the filter is applied.'
        ),
        required=True,
        source=CatalogSource(
            object_provides=ISyndicatableCollection.__identifier__
        ),
    )


class Assignment(base.Assignment):
    implements(ICollectionSearchPortlet)

    header = u""
    target_collection = None

    def __init__(
        self,
        header=u"",
        target_collection=None,
    ):
        self.header = header
        self.target_collection = target_collection

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u'Collection Search')


class Renderer(CollectionRenderer):
    render = ViewPageTemplateFile('collectionsearch.pt')

    @property
    def available(self):
        return True

    def header_title(self):
        if self.data.header:
            return self.data.header

        collection = self.collection(self.data.target_collection)
        if collection is None:
            return None
        else:
            return collection.Title()

    @property
    def value(self):
        val = u""
        if TEXT_IDX in self.request.form:
            val = safe_unicode(self.request.form.get(TEXT_IDX))
        return val

    @property
    def urlquery(self):
        urlquery = {}
        urlquery.update(self.request.form)
        for it in (TEXT_IDX, 'b_start', 'b_size', 'batch', 'sort_on', 'limit'):
            # Remove problematic url parameters
            if it in urlquery:
                del urlquery[it]
        return urlquery

    @property
    @memoize
    def collection(self):
        item = uuidToObject(self.data.target_collection)
        return item


class AddForm(z3cformhelper.AddForm):
    fields = field.Fields(ICollectionSearchPortlet)

    label = _(u"Add Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(z3cformhelper.EditForm):
    fields = field.Fields(ICollectionSearchPortlet)

    label = _(u"Edit Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )