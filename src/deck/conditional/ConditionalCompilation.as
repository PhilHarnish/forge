package conditional {
  public class ConditionalCompilation {
    public function ConditionalCompilation() {
      if (DEBUGGER::enabled) {
        trace("Debugger enabled.");
      } else if (TEST::enabled) {
        trace("Test enabled.");
      }

      if (false && TEST::enabled) {
        trace("Compound conditional not removed.");
      }

      foobar();
    }

    DEBUGGER::enabled
    public static function debugFunction():void {
    }

    TEST::enabled
    public static function testFunction():void {
    }

    DEBUGGER::enabled
    public static function foobar():void {
      trace("Debug version of foobar.");
    }

    DEBUGGER::disabled
    public static function foobar():void {
      trace("Production version of foobar.");
    }
  }
}
