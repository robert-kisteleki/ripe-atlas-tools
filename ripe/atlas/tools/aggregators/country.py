import json

from ripe.atlas.sagan import Result, ResultError

from ..probes import Probe
from .base import Aggregator as BaseAggregator


class CountryAggregator(BaseAggregator):

    def aggregate(self, results, probes):

        # Build "sagans" as a list of Sagan result objects: http://goo.gl/HKFkHE
        sagans = []
        for result in results:
            try:
                result = Result.get(
                    result,
                    on_error=Result.ACTION_IGNORE,
                    on_malformation=Result.ACTION_IGNORE
                )
                if not probes or result.probe_id in probes:
                    sagans.append(result)
            except ResultError:
                print("Bad result found: {}\n".format(json.dumps(result)))

        # Build a lookup dictionary of id:object for below
        probes = dict([
            (p.id, p) for p in Probe.get_from_api([r.probe_id for r in sagans])
        ])

        # Build the aggregate database
        db = {}
        for result in sagans:
            line = self.renderer.on_result(result, probes=probes)
            try:
                db.setdefault(probes[line.probe_id].country_code, []).append(
                    line
                )
            except KeyError:
                # For the very rare case that the results may have a probe in
                # there that's not yet available in the API.
                pass

        # Print everything out
        r = ""
        for country, lines in db.items():
            r += "{}\n".format(country)
            for line in lines:
                r += "  {}".format(line)
            r += "\n"

        return r