import java.io.File;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.json.JSONObject;
import org.testng.ITestResult;
import org.testng.TestListenerAdapter;
import org.testng.TestNG;

import io.mosip.testrig.apirig.dto.TestCaseDTO;
import io.mosip.testrig.apirig.report.EmailableReport;
import io.mosip.testrig.apirig.testrunner.BaseTestCase;
import io.mosip.testrig.apirig.utils.ConfigManager;
import io.mosip.testrig.apirig.utils.SkipTestCaseHandler;

/** Module-agnostic bridge test: -Dbridge.class, -Dfixtures, -Dfake.runner, -Dcomponent. */
public class OpenIDConformanceBridgeTest {
	static final String COMP = System.getProperty("component");
	static final File FIX = new File(System.getProperty("fixtures"));
	static final String FAKE = System.getProperty("fake.runner");
	static int failures = 0, seq = 0;
	static final String RUN = Long.toString(System.nanoTime(), 36);

	static void check(boolean ok, String what) {
		System.out.println((ok ? "PASS " : "FAIL ") + what);
		if (!ok)
			failures++;
	}

	@SuppressWarnings("unchecked")
	static void setCfg(String k, String v) throws Exception {
		Field f = ConfigManager.class.getDeclaredField("propertiesMap");
		f.setAccessible(true);
		((Map<String, Object>) f.get(null)).put(k, v);
	}

	@SuppressWarnings("unchecked")
	static List<String> skipList() throws Exception {
		Field f = SkipTestCaseHandler.class.getDeclaredField("testcaseToBeSkippedList");
		f.setAccessible(true);
		return (List<String>) f.get(null);
	}

	static class Res {
		String name, desc, msg, status, id;
		JSONObject rec;
	}

	static class Run {
		List<Res> results = new ArrayList<>();
		String report; // report file name
	}

	/** Runs the bridge against a JSONL file; template stem becomes config_name. */
	static Run run(String tag, Path jsonl, String stem, String strict) throws Exception {
		setCfg("conformance.runner.command", "sh " + FAKE + " " + jsonl);
		setCfg("conformance.plan.template", "plans/x/" + stem + ".json");
		setCfg("conformance.strict", strict);
		setCfg("conformance.runner.timeout", "60");
		setCfg("conformance.runner.dir", "");
		setCfg("injiCertifyBaseURL", "");
		setCfg("reportKnownIssueTestCases", "yes");
		setCfg("reportIgnoredTestCases", "no");
		BaseTestCase.environment = "local";
		// Report names must be unique per JVM: seq restarts at 1, so reports left in a reused testng-report/
		// by an earlier run (other fixture order) matched the prefix and were picked up as this run's report.
		String rn = "mosip-local-" + tag + "-" + (++seq) + "-" + RUN + "-report.html";
		System.setProperty("emailable.report2.name", rn);
		System.setProperty("testng.outpur.dir", "testng-report");

		TestNG t = new TestNG();
		t.setTestClasses(new Class[] { Class.forName(System.getProperty("bridge.class")) });
		TestListenerAdapter tla = new TestListenerAdapter();
		t.addListener(tla);
		t.addListener(new EmailableReport());
		t.setUseDefaultListeners(false);
		t.setOutputDirectory("testng-report");
		t.run();

		Run r = new Run();
		add(r, tla.getPassedTests(), "PASS");
		add(r, tla.getFailedTests(), "FAIL");
		add(r, tla.getSkippedTests(), "SKIP");
		r.results.sort(Comparator.comparing(x -> x.id));
		String prefix = rn.replace("-report.html", "-full-report_");
		for (File f : new File("testng-report").listFiles())
			if (f.getName().startsWith(prefix))
				r.report = f.getName();
		return r;
	}

	static void add(Run r, List<ITestResult> l, String status) {
		for (ITestResult x : l) {
			TestCaseDTO d = (TestCaseDTO) x.getParameters()[0];
			Res e = new Res();
			e.name = d.getTestCaseName();
			e.id = d.getUniqueIdentifier();
			e.desc = d.getDescription();
			e.status = status;
			e.msg = x.getThrowable() == null ? "" : String.valueOf(x.getThrowable().getMessage());
			e.rec = (JSONObject) x.getParameters()[1];
			if (!e.name.equals(x.getAttribute("TestCaseName")))
				check(false, "TestCaseName attribute for " + e.name);
			r.results.add(e);
		}
	}

	static String expected(String outcome, boolean ki) {
		switch (outcome) {
		case "pass": case "warning": return "PASS";
		case "review": case "skip": return "SKIP";
		case "fail": return ki ? "SKIP" : "FAIL";
		default: return "FAIL";
		}
	}

	static List<JSONObject> lines(Path p) throws Exception {
		List<JSONObject> l = new ArrayList<>();
		for (String s : Files.readAllLines(p))
			l.add(new JSONObject(s));
		return l;
	}

	public static void main(String[] args) throws Exception {
		Path tmp = Files.createTempDirectory("bridge");
		String kiName = "OIDF_" + COMP + "_oid4vci-1_0-issuer-metadata-test";

		// 1. every fixture of this component, in plan order, mapped per ADR-003
		File[] fxs = FIX.listFiles((d, n) -> n.endsWith(".jsonl"));
		java.util.Arrays.sort(fxs);
		for (File fx : fxs) {
			List<JSONObject> ls = lines(fx.toPath());
			String comp = ls.get(0).getString("component");
			String stem = fx.getName().replace(".jsonl", "");
			skipList().clear();
			Run r = run("c1", fx.toPath(), stem, "no");
			List<JSONObject> mods = new ArrayList<>();
			for (JSONObject o : ls)
				if (o.getString("type").equals("module"))
					mods.add(o);
			boolean ok = r.results.size() == mods.size();
			for (int i = 0; ok && i < mods.size(); i++) {
				Res e = r.results.get(i);
				ok = e.name.equals("OIDF_" + comp + "_" + mods.get(i).getString("module"))
						&& e.status.equals(expected(mods.get(i).getString("outcome"), false))
						&& !e.msg.startsWith("INFRA: ") == !mods.get(i).getString("outcome").equals("infra")
						&& e.id.equals(String.format("OIDF_%s_%02d", stem, i + 1));
			}
			check(ok, "case1 " + stem + ": " + mods.size() + " modules in order with mapped status");
			JSONObject c = ls.get(ls.size() - 1).getJSONObject("counts");
			Matcher m = Pattern.compile("T-(\\d+)_P-(\\d+)_S-(\\d+)_F-(\\d+)(?:_KI-(\\d+))?").matcher(String.valueOf(r.report));
			boolean fm = m.find() && Integer.parseInt(m.group(1)) == mods.size()
					&& Integer.parseInt(m.group(2)) == c.getInt("pass") + c.getInt("warning")
					&& Integer.parseInt(m.group(3)) == c.getInt("review") + c.getInt("skip")
					&& Integer.parseInt(m.group(4)) == c.getInt("fail") + c.getInt("infra")
					&& (m.group(5) == null || m.group(5).equals("0"));
			check(fm, "case1 " + stem + ": report filename counts " + r.report);
		}

		// 2. known issue (certify only)
		if ("certify".equals(COMP)) {
			skipList().clear();
			skipList().add(kiName);
			Run r = run("c2", FIX.toPath().resolve("certify-shim-off.jsonl"), "certify-shim-off", "no");
			Res e = r.results.get(0);
			check(e.name.equals(kiName) && e.status.equals("SKIP") && e.msg.contains("known issue"),
					"case2 KI test is SKIP with known-issue message: " + e.msg);
			check(String.valueOf(r.report).contains("T-14") && r.report.contains("F-13") && r.report.contains("_KI-1"),
					"case2 report filename T-14 F-13 KI-1: " + r.report);
			skipList().clear();
		}

		// 3. truncated stream: no end, last 3 modules missing
		Path src = FIX.toPath().resolve(COMP.equals("certify") ? "certify-shim-off.jsonl" : "verify-x509.jsonl");
		List<String> all = Files.readAllLines(src);
		Path trunc = tmp.resolve("trunc.jsonl");
		Files.write(trunc, all.subList(0, all.size() - 4));
		Run r3 = run("c3", trunc, "trunc", "no");
		long infra = r3.results.stream().filter(x -> x.status.equals("FAIL") && x.msg.startsWith("INFRA: ")
				&& x.msg.contains("runner exited without end record")).count();
		check(r3.results.size() == all.size() - 2 && infra == 3 && r3.results.get(r3.results.size() - 1).msg.startsWith("INFRA: "),
				"case3 truncated stream -> 3 synthetic INFRA failures (" + infra + ")");

		// 4. exit-2 stream
		Path ab = tmp.resolve("abort.jsonl");
		Files.write(ab, List.of(all.get(0),
				"{\"type\":\"end\",\"exit\":2,\"counts\":{\"pass\":0,\"warning\":0,\"review\":0,\"skip\":0,\"fail\":0,\"infra\":0},"
						+ "\"error\":\"environment has shim=true, config expects false\",\"export\":null,\"finished\":null}"));
		Run r4 = run("c4", ab, "abort", "no");
		int nmods = (int) all.stream().filter(s -> s.startsWith("{\"type\":\"module\"")).count();
		boolean ok4 = r4.results.size() == nmods && !r4.results.isEmpty();
		for (Res e : r4.results)
			ok4 &= e.status.equals("FAIL") && e.msg.startsWith("INFRA: environment has shim") && e.desc.contains("not observed");
		check(ok4, "case4 exit-2 -> all " + nmods + " plan modules INFRA, flags not observed");

		// 5. warning outcome
		Path wn = tmp.resolve("warn.jsonl");
		Files.write(wn, List.of(
				"{\"type\":\"plan\",\"component\":\"" + COMP + "\",\"run_id\":\"r\",\"plan_id\":\"p\",\"flags\":{\"certify_as_metadata_shim\":false,\"verify_evidence_upload\":null},\"modules\":[\"m1\"]}",
				"{\"type\":\"module\",\"module\":\"m1\",\"status\":\"FINISHED\",\"result\":\"WARNING\",\"outcome\":\"warning\",\"message\":\"w\",\"failed_conditions\":[],\"warnings\":[],\"log_url\":null,\"evidence\":[]}",
				"{\"type\":\"end\",\"exit\":0,\"counts\":{\"warning\":1},\"error\":null}"));
		check(run("c5a", wn, "warn", "no").results.get(0).status.equals("PASS"), "case5 warning -> PASS by default");
		check(run("c5b", wn, "warn", "yes").results.get(0).status.equals("FAIL"), "case5 warning -> FAIL with conformance.strict=yes");

		// 6. empty stream
		Path em = tmp.resolve("empty.jsonl");
		Files.write(em, new byte[0]);
		Run r6 = run("c6", em, "empty", "no");
		check(r6.results.size() == 1 && r6.results.get(0).name.equals("OIDF_" + COMP + "_runner")
				&& r6.results.get(0).status.equals("FAIL")
				&& r6.results.get(0).msg.startsWith("INFRA: runner produced no plan record (exit 0)"),
				"case6 no plan -> single OIDF_" + COMP + "_runner INFRA failure");

		System.out.println(failures == 0 ? "ALL PASSED" : failures + " FAILED");
		System.exit(failures == 0 ? 0 : 1);
	}
}
