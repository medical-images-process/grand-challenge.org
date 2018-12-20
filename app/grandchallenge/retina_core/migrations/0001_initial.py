# Generated by Django 2.1.3 on 2018-12-07 15:50

from django.db import migrations
from django.contrib.auth import get_user_model


def copy_ada_annotations_to_demo_forward(apps, schema_editor):
    # For debugging purposes
    Measurement = apps.get_model("annotations", "MeasurementAnnotation")
    BooleanClassification = apps.get_model(
        "annotations", "BooleanClassificationAnnotation"
    )
    PolygonAnnotationSet = apps.get_model(
        "annotations", "PolygonAnnotationSet"
    )
    SinglePolygon = apps.get_model("annotations", "SinglePolygonAnnotation")
    LandmarkAnnotationSet = apps.get_model(
        "annotations", "LandmarkAnnotationSet"
    )
    SingleLandmark = apps.get_model("annotations", "SingleLandmarkAnnotation")
    ETDRSGrid = apps.get_model("annotations", "ETDRSGridAnnotation")

    for model in (
        Measurement,
        BooleanClassification,
        PolygonAnnotationSet,
        LandmarkAnnotationSet,
        ETDRSGrid,
    ):
        for obj in model.objects.filter(grader__username="ada"):
            children = []
            if type(obj) == PolygonAnnotationSet:
                # copy children
                children = obj.singlepolygonannotation_set.all()
            if type(obj) == LandmarkAnnotationSet:
                children = obj.singlelandmarkannotation_set.all()

            obj.grader_id = get_user_model().objects.get(username="demo").id
            obj.pk = None
            obj.save()

            for child in children:
                child.pk = None
                child.annotation_set = obj
                child.save()


def copy_ada_annotations_to_demo_backward(apps, schema_editor):
    # For debugging purposes
    Measurement = apps.get_model("annotations", "MeasurementAnnotation")
    BooleanClassification = apps.get_model(
        "annotations", "BooleanClassificationAnnotation"
    )
    PolygonAnnotationSet = apps.get_model(
        "annotations", "PolygonAnnotationSet"
    )
    LandmarkAnnotationSet = apps.get_model(
        "annotations", "LandmarkAnnotationSet"
    )
    ETDRSGrid = apps.get_model("annotations", "ETDRSGridAnnotation")

    for model in (
        Measurement,
        BooleanClassification,
        PolygonAnnotationSet,
        LandmarkAnnotationSet,
        ETDRSGrid,
    ):
        model.objects.filter(grader__username="demo").delete()


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunPython(
            copy_ada_annotations_to_demo_forward,
            copy_ada_annotations_to_demo_backward,
        )
    ]
